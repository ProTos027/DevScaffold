
import json
import re

def format_gemini_error(e: Exception) -> str:
    """
    Extracts the human-readable 'message' from a Gemini API error.
    Handles ServerError, ClientError, and generic exceptions.
    """
    error_str = str(e)
    
    # Try to extract from JSON-like structure in the error string
    # Pattern: {'error': {'code': ..., 'message': '...', 'status': '...'}}
    try:
        # Simplest case: if it's already a dict-like string, try to find the message
        if "'message':" in error_str or '"message":' in error_str:
            # Attempt to extract using regex to be resilient to surrounding text
            match = re.search(r"['\"]message['\"]: ['\"](.*?)['\"]", error_str)
            if match:
                return match.group(1)
                
        # Fallback 1: Check for common status codes if parsing fails
        if "503" in error_str:
            return "The model is overloaded (503). Please try again later."
        if "429" in error_str:
            return "API quota exhausted (429). Please try again later or use a different key."
        if "401" in error_str:
            return "Invalid API key (401). Please check your vault settings."
            
    except Exception:
        pass
        
    # Final fallback: return the original string but truncated
    return error_str[:200]
