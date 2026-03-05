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
    """If a backend stack is chosen, an API type (REST, GraphQL, etc.) must be specified."""
    
    @staticmethod
    def validate(spec: IntentSpecSchema) -> Tuple[bool, str]:
        backend = spec.stack.backend.framework
        if backend != 'none' and spec.api_type == 'none':
            return False, "Backend selected but no API type (REST/GraphQL) specified."
        return True, ""


class DatabaseRequiresEntities(ValidationRule):
    """If a database is selected, at least one data entity must be defined."""
    
    @staticmethod
    def validate(spec: IntentSpecSchema) -> Tuple[bool, str]:
        db = spec.stack.database.framework
        if db and db != 'none' and not spec.data_entities:
            return False, "Database selected but no data entities defined."
        return True, ""


class AuthenticationRequiresUserEntity(ValidationRule):
    """If authentication is enabled, a 'User' or 'Account' entity must exist with mandatory fields."""
    
    @staticmethod
    def validate(spec: IntentSpecSchema) -> Tuple[bool, str]:
        if spec.auth_method == 'none':
            return True, ""
            
        user_entities = [e for e in spec.data_entities if e.name.lower() in ['user', 'account', 'profile']]
        if not user_entities:
            return False, f"Authentication ({spec.auth_method}) enabled but no 'User' or 'Account' entity found in schema."
            
        # Deep Validation: Check for minimal fields required for auth
        for entity in user_entities:
            field_names = [f.lower() for f in entity.fields]
            # Must have an identifier and a secret/credential field
            has_id = any('username' in f or 'email' in f or 'id' in f for f in field_names)
            has_secret = any('password' in f or 'secret' in f or 'token' in f or 'hash' in f for f in field_names)
            
            if has_id and has_secret:
                return True, ""
                
        return False, f"User-related entity found, but lacks mandatory fields for {spec.auth_method} (e.g., username/email and password)."


# Registry of active architectural validation rules
VALIDATION_RULES: List[type[ValidationRule]] = [
    BackendRequiresAPIType,
    DatabaseRequiresEntities,
    AuthenticationRequiresUserEntity,
]


def validate_intent_spec(spec: IntentSpecSchema) -> Tuple[bool, List[str]]:
    """
    Validate an Intent Spec against core structural rules.
    Returns (is_valid, list_of_error_messages).
    """
    errors = []
    
    for rule_class in VALIDATION_RULES:
        is_valid, error_message = rule_class.validate(spec)
        if not is_valid:
            errors.append(error_message)
    
    return (len(errors) == 0, errors)
