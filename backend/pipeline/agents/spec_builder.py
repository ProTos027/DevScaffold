"""
Spec Builder Agent - Converts user prompt to Intent Spec using Google GenAI SDK.
"""
import json
from core.logger import get_logger
from ..schemas import IntentSpecSchema
from ..utils.gemini import gemini_call_with_retry, format_gemini_error

logger = get_logger(__name__)


SPEC_BUILDER_SYSTEM_PROMPT = """You are an Intent Specification Parser for DevScaffold.
Your only job: convert a natural language project description into a valid IntentSpecSchema JSON.

── OUTPUT CONTRACT ──────────────────────────────────────────────────────────
- Output ONLY valid JSON. No explanations, no markdown, no prose.
- All schema fields are mandatory. Use empty strings/lists for absent data.

── RESILIENCE & DEFAULTS ────────────────────────────────────────────────────
- Vague/short/nonsense prompts: make a BEST-GUESS for a standard project of that type. Do NOT fail.
- Set `vague_intent: true` and describe your assumptions in `explanation` when guessing.
- Default backend: "fastapi".
- api_type: Default to "rest". Only use "graphql" if requested.

── CASCADE RULES (LOGICAL CHAINING) ─────────────────────────────────────────
- **Rule 1 (Auth)**: If `auth_method` is 'jwt' or 'session' → MUST add "authentication" to the `features` list.
- **Rule 2 (User)**: If "authentication" is in `features` → MUST add a "User" entity to `data_entities`.
- **Rule 3 (User Fields)**: The "User" entity MUST include: `id`, `username`, `email`, `hashed_password`, `is_active`, `created_at`.
- Failures to propagate these dependencies result in broken project generation.

── FEATURE RULES ─────────────────────────────────────────────────────────────
- Include ONLY features logically required.
- **Prefer Canonical Names**: Always use these strings if they apply: `authentication`, `user_profiles`, `file_upload`, `notifications`, `search`, `admin_panel`. 
- Do NOT use synonyms like "auth", "login", or "user_meta" for the above.
- You can add custom feature names for anything outside this list.

── DATA ENTITY RULES ────────────────────────────────────────────────────────
- Include ONLY entities logically required.
- For every entity: include ALL fields with types. Always include `id` and `created_at`.
- Write FK fields explicitly: use `author_id: int`, never just "author".
- Do NOT abbreviate field names (e.g. write `membership_type` not `mem_typ`).

── STACK RULES ──────────────────────────────────────────────────────────────
- Framework mapping: Java/Spring Boot → "springboot" | FastAPI → "fastapi" | Express/Node → "express" | Django → "django"
- Support: React, Vue, Svelte, Next.js for frontend.
- `backend_version`, `frontend_version`, `database_version`: ONLY include if the user explicitly states a version (e.g. "FastAPI 0.109"). Use null otherwise.
- If a frontend framework is requested, you MUST include a backend.

── KNOWLEDGE BASE & RAG PRECEDENCE ──────────────────────────────────────────
If a "DOMAIN KNOWLEDGE" section appears, treat it as MANDATORY GUIDELINES for domain logic.
- **Precedence**: RAG knowledge overrides your general training for naming/conventions.
- **Constraint**: RAG knowledge CANNOT override structural rules (e.g., mandatory `id` fields or Cascade Rules).
"""


def build_spec_from_prompt(
    prompt: str,
    model_name: str,
    rag_service=None,
    on_exhaustion=None
) -> IntentSpecSchema:
    """
    Use Google GenAI SDK to generate Intent Spec from user prompt with structured output.
    """
    if not prompt or not prompt.strip():
        raise ValueError("Prompt is empty or only whitespace. Cannot build intent specification.")


    
    if not model_name.startswith("gemini-"):
        logger.warning(f"Invalid model_name '{model_name}'. Falling back to 'gemini-2.5-flash'.")
        model_name = "gemini-2.5-flash"

    # ── RAG: retrieve domain patterns before deciding data entities ───────────
    domain_context = ""
    if rag_service:
        try:
            domain_context = rag_service.retrieve(
                f"data entities fields {prompt[:300]}",
                top_k=3
            )
        except Exception as e:
            logger.warning(f"RAG retrieval in spec_builder failed (non-fatal): {e}")

    system_instruction = SPEC_BUILDER_SYSTEM_PROMPT
    if domain_context:
        system_instruction += f"\n\nDOMAIN KNOWLEDGE FROM KNOWLEDGE BASE:\n{domain_context}"

    try:
        logger.debug(f"User Prompt: {prompt[:200]}...")
        
        response = gemini_call_with_retry(
            model_name,
            contents=f"USER INPUT: {prompt}",
            config={
                "system_instruction": system_instruction,
                "response_mime_type": "application/json",
                "response_json_schema": IntentSpecSchema.model_json_schema(),
            },
            on_exhaustion=on_exhaustion
        )
        
        content = response.candidates[0].content.parts[0].text
        logger.debug(f"Raw Response: {content}")
        
        spec_dict = json.loads(content)
        spec = IntentSpecSchema(**spec_dict)
        
        return spec
        
    except Exception as e:
        clean_msg = format_gemini_error(e)
        logger.error(f"SPEC BUILDER ERROR: {clean_msg}")
        raise ValueError(clean_msg)
