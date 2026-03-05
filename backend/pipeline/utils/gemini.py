import time
from google import genai
from core.logger import get_logger
from ..rotation_manager import RotationManager

logger = get_logger(__name__)

# Module-level centralized client
_client = None

def set_client(api_key: str) -> None:
    """Initialize or update the shared GenAI client."""
    global _client
    _client = genai.Client(api_key=api_key)

def rotate_client(user, provider: str):
    """Picks the next available key for user/provider and updates the shared client."""
    new_key_obj = RotationManager.get_best_key(user, provider=provider)
    if new_key_obj:
        api_key = new_key_obj.get_api_key()
        set_client(api_key)
        logger.info(f"Rotation successful. Continuing with '{new_key_obj.name}'.")
        return new_key_obj
    logger.error("Mid-Run Rotation failed: No more available keys.")
    return None

def format_gemini_error(e: Exception) -> str:
    """
    Extracts the human-readable 'message' from a Gemini API error.
    """
    message = getattr(e, 'message', str(e))
    return message[:200]

def _is_retryable(e: Exception) -> bool:
    """
    Return True if this is a 429 (quota) or 503 (overload) error that should be retried.
    """
    code = getattr(e, 'code', None)
    return code in (429, 503)

def _extract_retry_seconds(e: Exception) -> float | None:
    """
    Parse the recommended wait duration from a Gemini quota/overload error.
    """
    details = getattr(e, 'details', None)
    try:
        if isinstance(details, dict):
            error_details = details['error']['details']
            for item in error_details:
                if 'RetryInfo' in item.get('@type', ''):
                    delay = item['retryDelay']
                    if delay.endswith('s'):
                        return float(delay[:-1]) + 1.0
    except (KeyError, TypeError, ValueError):
        pass

    return None

def gemini_call_with_retry(model_name: str, contents, config: dict, max_retries: int = 5, on_exhaustion=None):
    """
    Wrapper around _client.models.generate_content() with automatic retry.
    """
    for attempt in range(max_retries + 1):
        config.setdefault("temperature", 0.2)

        try:
            return _client.models.generate_content(
                model=model_name,
                contents=contents,
                config=config,
            )
        except Exception as e:
            if not _is_retryable(e):
                raise

            wait = _extract_retry_seconds(e)

            # Daily Quota Circuit Breaker
            message = getattr(e, 'message', '').lower()
            if "perday" in message or "daily" in message:
                if on_exhaustion:
                    logger.info("Daily Limit hit. Attempting Mid-Run Rotation...")
                    on_exhaustion()
                    if _client:
                        return gemini_call_with_retry(model_name, contents, config, max_retries - attempt, on_exhaustion)

                raise Exception(getattr(e, 'message', str(e))) from e

            if attempt >= max_retries:
                raise

            wait = wait or 5.0
            logger.warning(f"Gemini {getattr(e, 'code', 'err')} - Sleeping {wait:.1f}s (attempt {attempt+1}/{max_retries})...")
            time.sleep(wait)

def gemini_embed_with_retry(model_name: str, contents, max_retries: int = 5, on_exhaustion=None):
    """
    Wrapper around _client.models.embed_content() with automatic retry.
    """
    for attempt in range(max_retries + 1):
        try:
            return _client.models.embed_content(
                model=model_name,
                contents=contents,
            )
        except Exception as e:
            if not _is_retryable(e):
                raise

            wait = _extract_retry_seconds(e)

            # Daily Quota Circuit Breaker
            message = getattr(e, 'message', '').lower()
            if "perday" in message or "daily" in message:
                if on_exhaustion:
                    logger.info("Daily Limit hit on Embedding. Attempting Mid-Run Rotation...")
                    on_exhaustion()
                    if _client:
                        return gemini_embed_with_retry(model_name, contents, max_retries - attempt, on_exhaustion)

                raise Exception(getattr(e, 'message', str(e))) from e

            if attempt >= max_retries:
                raise

            wait = wait or 5.0
            logger.warning(f"Gemini Embed {getattr(e, 'code', 'err')} - Sleeping {wait:.1f}s (attempt {attempt+1}/{max_retries})...")
            time.sleep(wait)
