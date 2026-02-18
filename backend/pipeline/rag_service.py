"""
RAG Knowledge Base Service.
Uses Google GenAI embeddings + numpy cosine similarity for framework-specific retrieval.
Zero extra dependencies — uses google-genai (already installed) and numpy.
"""
import os
import json
import hashlib
from pathlib import Path
from typing import List, Dict, Optional

import numpy as np
from google import genai

# Path to knowledge base directory
KNOWLEDGE_DIR = Path(__file__).parent.parent / 'knowledge'
# Path for cached embeddings
CACHE_DIR = Path(__file__).parent.parent / 'knowledge' / '.cache'


class RAGService:
    """
    Retrieval-Augmented Generation service.
    Loads markdown docs from knowledge/, embeds them, and retrieves 
    relevant chunks for injection into agent system prompts.
    """
    
    def __init__(self, api_key: str, embedding_model: str = "models/gemini-embedding-001"):
        self.client = genai.Client(api_key=api_key)
        self.embedding_model = embedding_model
        self.chunks: List[Dict] = []       # {"text": ..., "source": ..., "framework": ...}
        self.embeddings: np.ndarray = None  # (N, dim) matrix
        self._loaded = False
    
    def load(self, frameworks: List[str] = None):
        """
        Load and embed knowledge base documents.
        Only loads docs for specified frameworks + 'general' for efficiency.
        """
        if self._loaded:
            return
        
        self.chunks = []
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
                self.chunks.extend(file_chunks)
        
        if not self.chunks:
            self._loaded = True
            return
        
        # Check cache
        cache_key = self._cache_key([c['text'] for c in self.chunks])
        cached = self._load_cache(cache_key)
        
        if cached is not None:
            self.embeddings = cached
        else:
            # Embed all chunks via Google API
            texts = [c['text'] for c in self.chunks]
            self.embeddings = self._embed_batch(texts)
            self._save_cache(cache_key, self.embeddings)
        
        self._loaded = True
    
    def retrieve(self, query: str, top_k: int = 3) -> str:
        """
        Retrieve the top-k most relevant knowledge chunks for a query.
        Returns a formatted string ready for prompt injection.
        """
        if not self._loaded or self.embeddings is None or len(self.chunks) == 0:
            return ""
        
        # Embed query
        query_embedding = self._embed_batch([query])
        
        # Cosine similarity
        similarities = self._cosine_similarity(query_embedding, self.embeddings)[0]
        
        # Top-k indices
        top_indices = np.argsort(similarities)[-top_k:][::-1]
        
        # Build context string
        results = []
        for idx in top_indices:
            if similarities[idx] < 0.3:  # Relevance threshold
                continue
            chunk = self.chunks[idx]
            results.append(f"[{chunk['framework']}/{chunk['source']}]\n{chunk['text']}")
        
        if not results:
            return ""
        
        return "KNOWLEDGE BASE CONTEXT:\n" + "\n---\n".join(results)
    
    def _chunk_markdown(self, text: str, source: str, framework: str, max_chunk_size: int = 500) -> List[Dict]:
        """Split markdown by ## headers into semantic chunks."""
        chunks = []
        current_chunk = []
        current_size = 0
        
        for line in text.split('\n'):
            # Split on ## headers (keep the header with its section)
            if line.startswith('## ') and current_chunk:
                chunk_text = '\n'.join(current_chunk).strip()
                if chunk_text:
                    chunks.append({
                        'text': chunk_text,
                        'source': source,
                        'framework': framework
                    })
                current_chunk = [line]
                current_size = len(line)
            else:
                current_chunk.append(line)
                current_size += len(line)
                
                # Also split if chunk gets too large
                if current_size > max_chunk_size and not line.startswith('#'):
                    chunk_text = '\n'.join(current_chunk).strip()
                    if chunk_text:
                        chunks.append({
                            'text': chunk_text,
                            'source': source,
                            'framework': framework
                        })
                    current_chunk = []
                    current_size = 0
        
        # Last chunk
        if current_chunk:
            chunk_text = '\n'.join(current_chunk).strip()
            if chunk_text:
                chunks.append({
                    'text': chunk_text,
                    'source': source,
                    'framework': framework
                })
        
        return chunks
    
    def _embed_batch(self, texts: List[str]) -> np.ndarray:
        """Embed a batch of texts using Google GenAI."""
        # API supports batches up to 100
        all_embeddings = []
        
        for i in range(0, len(texts), 100):
            batch = texts[i:i+100]
            result = self.client.models.embed_content(
                model=self.embedding_model,
                contents=batch
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
        """Generate a cache key from the content hash."""
        content = '||'.join(texts)
        return hashlib.md5(content.encode()).hexdigest()
    
    def _load_cache(self, cache_key: str) -> Optional[np.ndarray]:
        """Load cached embeddings if they exist."""
        cache_file = CACHE_DIR / f'{cache_key}.npy'
        if cache_file.exists():
            try:
                return np.load(str(cache_file))
            except Exception:
                return None
        return None
    
    def _save_cache(self, cache_key: str, embeddings: np.ndarray):
        """Save embeddings to cache."""
        CACHE_DIR.mkdir(parents=True, exist_ok=True)
        cache_file = CACHE_DIR / f'{cache_key}.npy'
        try:
            np.save(str(cache_file), embeddings)
        except Exception:
            pass  # Cache failures are non-fatal
