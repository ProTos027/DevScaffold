"""
Prompt Expander Agent — Dynamic Domain Knowledge Generation.
"""
from core.logger import get_logger
from ..utils.gemini import gemini_call_with_retry

logger = get_logger(__name__)


EXPANDER_SYSTEM_PROMPT = """You are a senior software engineering consultant.
Given a project description, generate a concise, dense domain knowledge reference 
that would help a software engineer implement it correctly.

── OUTPUT FORMAT ─────────────────────────────────────────────────────────────
Write ONLY structured markdown sections using ## headers. No preamble or sign-off.

## Relevant Libraries & Tools
List the best-fit libraries for this project domain with brief usage examples.
Include both backend (Python/JS) and frontend libraries if applicable.

## Standard Data Models
Key fields and relationships for the domain's core entities.

## API Design Conventions
Standard endpoint patterns, HTTP methods, and payload formats for this domain.

## Common Gotchas & Best Practices
Known pitfalls, edge cases, and implementation patterns specific to this domain.
"""


def expand_prompt_to_domain_knowledge(
    user_prompt: str,
    model_name: str,
    on_exhaustion=None
) -> str:
    """
    Call Gemini to expand the user's project prompt into a dense domain knowledge
    """
    if not model_name.startswith("gemini-"):
        logger.warning(f"Invalid model_name '{model_name}'. Falling back to 'gemini-2.5-flash'.")
        model_name = "gemini-2.5-flash"

    try:
        response = gemini_call_with_retry(
            model_name,
            contents=f"Project Description:\n{user_prompt}\n\nGenerate the domain knowledge reference:",
            config={
                "system_instruction": EXPANDER_SYSTEM_PROMPT,
                "temperature": 0.2,
            },
            on_exhaustion=on_exhaustion
        )
        return response.candidates[0].content.parts[0].text
    except Exception as e:
        logger.warning(f"Prompt expansion failed (non-fatal): {e}")
        return ""
