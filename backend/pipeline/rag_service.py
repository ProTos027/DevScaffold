"""
RAG Knowledge Base Service.
Zero extra dependencies — uses google-genai (already installed) and numpy.
"""
import hashlib
import numpy as np
from google import genai
from pathlib import Path
from core.logger import get_logger
from typing import List, Dict, Optional

logger = get_logger(__name__)

# Path to knowledge base directory
KNOWLEDGE_DIR = Path(__file__).parent.parent / 'knowledge'
# Path to domain knowledge files
DOMAINS_DIR = KNOWLEDGE_DIR / 'domains'
# Path for cached static embeddings
CACHE_DIR = Path(__file__).parent.parent / 'knowledge' / '.cache'


from . import utils as pipeline_utils

class RAGService:
    """
    Retrieval-Augmented Generation service focused on Static Knowledge.
    """

    def __init__(self, embedding_model: str = "models/gemini-embedding-001"):
        self.embedding_model = embedding_model

        self._static_chunks: List[Dict] = []
        self._static_embeddings: Optional[np.ndarray] = None
        self._loaded = False
        self._loaded_frameworks: List[str] = []

    def load(self, frameworks: List[str] = None, on_exhaustion=None):
        """
        Load and embed static knowledge base documents.
        Loads docs for specified frameworks and always 'general'.
        Uses .npy cache keyed by content hash to avoid re-embedding.
        """
        requested_fw = sorted([f.lower() for f in frameworks]) if frameworks else []
        if self._loaded and requested_fw == self._loaded_frameworks:
            logger.warning(f" RAG: Frameworks {requested_fw} already loaded. Skipping.")
            return

        logger.info(f" RAG: Loading frameworks={requested_fw}")
        self._loaded_frameworks = requested_fw
        self._loaded_domains = []

        self._static_chunks = []
        target_dirs = []

        # Always include general best practices
        general_dir = KNOWLEDGE_DIR / 'general'
        if general_dir.exists():
            target_dirs.append(('general', general_dir))

        # Add framework-specific dirs
        if frameworks:
            for fw in frameworks:
                fw_dir = KNOWLEDGE_DIR / fw.lower()
                if fw_dir.exists():
                    target_dirs.append((fw.lower(), fw_dir))

        # Load and chunk markdown files
        for framework, dir_path in target_dirs:
            for md_file in dir_path.glob('*.md'):
                text = md_file.read_text(encoding='utf-8')
                file_chunks = self._chunk_markdown(text, source=md_file.name, framework=framework)
                self._static_chunks.extend(file_chunks)

        if not self._static_chunks:
            logger.warning(f" RAG: No markdown documentation found for {target_dirs}. Knowledge base will be empty.")
            self._loaded = True
            return

        # Check cache
        cache_key = self._cache_key([c['text'] for c in self._static_chunks])
        cached = self._load_cache(cache_key)

        if cached is not None:
            self._static_embeddings = cached
        else:
            texts = [c['text'] for c in self._static_chunks]
            self._static_embeddings = self._embed_batch(texts, on_exhaustion=on_exhaustion)
            self._save_cache(cache_key, self._static_embeddings)

        self._loaded = True

    def add_text(self, text: str, source: str = 'project_context', on_exhaustion=None) -> None:
        """
        Dynamically embed arbitrary text into the retrieval corpus.
        Used to inject LLM-expanded domain knowledge at runtime.
        Merges with the existing static embeddings.
        """
        if not text or not text.strip():
            return
        new_chunks = self._chunk_markdown(text, source=source, framework='dynamic')
        if not new_chunks:
            return
        new_texts = [c['text'] for c in new_chunks]
        new_embeddings = self._embed_batch(new_texts, on_exhaustion=on_exhaustion)
        self._static_chunks.extend(new_chunks)
        if self._static_embeddings is not None:
            self._static_embeddings = np.vstack([self._static_embeddings, new_embeddings])
        else:
            self._static_embeddings = new_embeddings
        logger.info(f"RAG: Injected {len(new_chunks)} dynamic chunk(s) from '{source}'")

    def retrieve(self, query: str, top_k: int = 3, on_exhaustion=None) -> str:
        """
        Retrieve top-k most relevant static knowledge chunks.
        Returns a formatted string ready for prompt injection.
        """
        if not self._loaded or self._static_embeddings is None or len(self._static_chunks) == 0:
            return ""

        query_emb = self._embed_batch([query], on_exhaustion=on_exhaustion)
        sims = self._cosine_similarity(query_emb, self._static_embeddings)[0]
        top_idx = np.argsort(sims)[-top_k:][::-1]

        results = []
        for idx in top_idx:
            if sims[idx] < 0.5: # require more specific matches
                continue
            chunk = self._static_chunks[idx]
            results.append(f"[{chunk['framework']}/{chunk['source']}]\n{chunk['text']}")

        if not results:
            return ""
        return "KNOWLEDGE BASE CONTEXT (Framework Reference):\n" + "\n---\n".join(results)

    # Internal helpers
    def _chunk_markdown(self, text: str, source: str, framework: str, max_chunk_size: int = 600) -> List[Dict]:
        """Split markdown by ## headers into semantic chunks."""
        chunks = []
        current_chunk = []
        current_size = 0

        for line in text.split('\n'):
            if line.startswith('## ') and current_chunk:
                chunk_text = '\n'.join(current_chunk).strip()
                if chunk_text:
                    chunks.append({'text': chunk_text, 'source': source, 'framework': framework})
                current_chunk = [line]
                current_size = len(line)
            else:
                current_chunk.append(line)
                current_size += len(line)
                if current_size > max_chunk_size and not line.startswith('#'):
                    chunk_text = '\n'.join(current_chunk).strip()
                    if chunk_text:
                        chunks.append({'text': chunk_text, 'source': source, 'framework': framework})
                    current_chunk = []
                    current_size = 0

        # Last chunk
        if current_chunk:
            chunk_text = '\n'.join(current_chunk).strip()
            if chunk_text:
                chunks.append({'text': chunk_text, 'source': source, 'framework': framework})

        return chunks

    def _embed_batch(self, texts: List[str], on_exhaustion=None) -> np.ndarray:
        """Embed a batch of texts using centralized utils client with retry."""
        all_embeddings = []
        for i in range(0, len(texts), 100):
            batch = texts[i:i+100]
            result = pipeline_utils.gemini_embed_with_retry(
                model_name=self.embedding_model,
                contents=batch,
                on_exhaustion=on_exhaustion
            )
            for embedding in result.embeddings:
                all_embeddings.append(embedding.values)
        return np.array(all_embeddings, dtype=np.float32)

    def _cosine_similarity(self, a: np.ndarray, b: np.ndarray) -> np.ndarray:
        """Compute cosine similarity between two sets of vectors."""
        a_norm = a / (np.linalg.norm(a, axis=1, keepdims=True) + 1e-10)
        b_norm = b / (np.linalg.norm(b, axis=1, keepdims=True) + 1e-10)
        return a_norm @ b_norm.T

    def _cache_key(self, texts: List[str]) -> str:
        content = '||'.join(texts)
        return hashlib.md5(content.encode()).hexdigest()

    def _load_cache(self, cache_key: str) -> Optional[np.ndarray]:
        cache_file = CACHE_DIR / f'{cache_key}.npy'
        if cache_file.exists():
            try:
                return np.load(str(cache_file))
            except Exception as e:
                logger.warning(f" RAG: Failed to load cache {cache_file}: {e}")
                return None
        logger.warning(f" RAG: Cache miss for {cache_key}.")
        return None

    def _save_cache(self, cache_key: str, embeddings: np.ndarray):
        CACHE_DIR.mkdir(parents=True, exist_ok=True)
        cache_file = CACHE_DIR / f'{cache_key}.npy'
        try:
            np.save(str(cache_file), embeddings)
        except Exception as e:
            logger.warning(f" RAG: Failed to save cache {cache_file}: {e}")
