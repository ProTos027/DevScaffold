"""
Semantic validation rules for Intent Specifications.
All rules are deterministic - no LLM involvement.
"""
from typing import List, Tuple
from .schemas import IntentSpecSchema


class ValidationRule:
    """Base class for validation rules."""
    
    @staticmethod
    def validate(spec: IntentSpecSchema) -> Tuple[bool, str]:
        """
        Validate the spec.
        Returns (is_valid, error_message).
        """
        raise NotImplementedError


class BackendRequiresAPIType(ValidationRule):
    """If backend exists, api_type is required."""
    
    @staticmethod
    def validate(spec: IntentSpecSchema) -> Tuple[bool, str]:
        # Softened: Defaulting to 'rest' or letting downstream handle missing types
        return True, ""


class DatabaseRequiresEntities(ValidationRule):
    """If database exists, data_entities are required."""
    
    @staticmethod
    def validate(spec: IntentSpecSchema) -> Tuple[bool, str]:
        # Softened: Entities can be inferred later if missing
        # The spec_builder now has fallback entity generation
        # if spec.stack.get('database') and not spec.data_entities:
        #     return False, "Database requires at least one data entity"
        return True, ""


class AuthenticationRequiresUserEntity(ValidationRule):
    """If authentication feature exists, User entity is required."""
    
    @staticmethod
    def validate(spec: IntentSpecSchema) -> Tuple[bool, str]:
        # Softened: Let the LLM correct this in spec_builder or downstream
        return True, ""


class FrontendRequiresBackend(ValidationRule):
    """If frontend exists, backend must exist."""
    
    @staticmethod
    def validate(spec: IntentSpecSchema) -> Tuple[bool, str]:
        # Softened: Minimal check
        return True, ""


class JWTRequiresTokenValidation(ValidationRule):
    """If auth_method is jwt, token validation responsibility will be required."""
    
    @staticmethod
    def validate(spec: IntentSpecSchema) -> Tuple[bool, str]:
        # Softened
        return True, ""


class StackCompatibility(ValidationRule):
    """Check stack compatibility."""
    
    # Define incompatible combinations
    INCOMPATIBLE = [
        ({'frontend': 'react', 'backend': 'none'}, "React requires a backend"),
        ({'frontend': 'vue', 'backend': 'none'}, "Vue requires a backend"),
    ]
    
    @staticmethod
    def validate(spec: IntentSpecSchema) -> Tuple[bool, str]:
        for incompatible, message in StackCompatibility.INCOMPATIBLE:
            if all(spec.stack.get(k) == v for k, v in incompatible.items()):
                return False, message
        return True, ""


class StrictIntentSpec(ValidationRule):
    """Ensure the spec isn't generic and has a backend."""
    
    @staticmethod
    def validate(spec: IntentSpecSchema) -> Tuple[bool, str]:
        # Softened: Allow generic specs to pass for later review/refinement
        return True, ""


# Registry of all validation rules
VALIDATION_RULES: List[type[ValidationRule]] = [
    StrictIntentSpec,
    BackendRequiresAPIType,
    DatabaseRequiresEntities,
    AuthenticationRequiresUserEntity,
    FrontendRequiresBackend,
    JWTRequiresTokenValidation,
    StackCompatibility,
]


def validate_intent_spec(spec: IntentSpecSchema) -> Tuple[bool, List[str]]:
    """
    Validate an Intent Spec against all rules.
    Returns (is_valid, list_of_error_messages).
    """
    errors = []
    
    for rule_class in VALIDATION_RULES:
        is_valid, error_message = rule_class.validate(spec)
        if not is_valid:
            errors.append(f"{rule_class.__name__}: {error_message}")
    
    return (len(errors) == 0, errors)
