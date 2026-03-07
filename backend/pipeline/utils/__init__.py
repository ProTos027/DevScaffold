"""
Pipeline utilities package.
Re-exports all helpers so callers can do:
    from . import utils as pipeline_utils
    pipeline_utils.gemini_call_with_retry(...)
    pipeline_utils.gemini_embed_with_retry(...)
"""
from .gemini import (
    set_client,
    rotate_client,
    gemini_call_with_retry,
    gemini_embed_with_retry,
    format_gemini_error,
)
from .graph import topological_sort  # noqa: F401 (export for consumers)
