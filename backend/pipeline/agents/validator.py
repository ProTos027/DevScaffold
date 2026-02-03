"""
Validator Agent - Deterministic rule-based validation (no LLM).
"""
from typing import List
from ..schemas import IntentSpecSchema
from ..rules import validate_intent_spec


class ValidationResult:
    """Result of validation."""
    
    def __init__(self, is_valid: bool, errors: List[str]):
        self.is_valid = is_valid
        self.errors = errors
    
    def __bool__(self):
        return self.is_valid


def validate_spec(spec: IntentSpecSchema) -> ValidationResult:
    """
    Validate an Intent Spec using deterministic rules.
    No LLM involvement - pure rule checking.
    
    Args:
        spec: IntentSpecSchema to validate
    
    Returns:
        ValidationResult with is_valid flag and list of errors
    """
    is_valid, errors = validate_intent_spec(spec)
    return ValidationResult(is_valid, errors)
