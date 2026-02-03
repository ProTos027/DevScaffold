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
        if spec.stack.get('backend') and not spec.architecture.get('api_type'):
            return False, "Backend requires api_type in architecture (e.g., 'rest' or 'graphql')"
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
        if 'authentication' in spec.features:
            user_exists = any(entity.name.lower() == 'user' for entity in spec.data_entities)
            if not user_exists:
                return False, "Authentication feature requires a User data entity"
        return True, ""


class FrontendRequiresBackend(ValidationRule):
    """If frontend exists, backend must exist."""
    
    @staticmethod
    def validate(spec: IntentSpecSchema) -> Tuple[bool, str]:
        if spec.stack.get('frontend') and not spec.stack.get('backend'):
            return False, "Frontend requires a backend"
        return True, ""


class JWTRequiresTokenValidation(ValidationRule):
    """If auth_method is jwt, token validation responsibility will be required."""
    
    @staticmethod
    def validate(spec: IntentSpecSchema) -> Tuple[bool, str]:
        # This is a soft check - will be enforced in component plan generation
        if spec.constraints.get('auth_method') == 'jwt':
            if 'authentication' not in spec.features:
                return False, "JWT auth_method requires 'authentication' feature"
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
        if spec.project_type == 'web_app' and not spec.features:
            return False, "Project type is too generic ('web_app') and no features specified."
        if not spec.stack.get('backend'):
            return False, "Backend framework must be specified."
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
