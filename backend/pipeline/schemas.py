"""
Pydantic models/schemas for the DevScaffold pipeline.
These define the strict structure for Intent Specs, Component Plans, etc.
"""
from pydantic import BaseModel, Field, model_validator
from typing import List, Dict, Optional, Literal

# for file generation
class GeneratedFile(BaseModel):
    """Schema for a single generated file."""
    path: str
    content: str
    language: str

class CrossLayerContractSchema(BaseModel):
    """Typed synchronization contract between generation phases."""
    api_base_url: Optional[str] = Field(
        default="http://localhost:8000",
        description="The full base URL the frontend uses to reach the backend, e.g. 'http://localhost:8000'"
    )
    auth_token_field: Optional[str] = Field(
        default="access",
        description="The EXACT JSON key in the login response that holds the bearer token, e.g. 'access'. Frontend MUST read response.data[this_field]."
    )
    auth_header_format: Optional[str] = Field(
        default="Bearer {token}",
        description="The format of the Authorization header, e.g. 'Bearer {token}'"
    )
    db_url_env_var: Optional[str] = Field(
        default="DATABASE_URL",
        description="The .env variable name for the database connection string"
    )
    frontend_port: Optional[str] = Field(
        default="",
        description="Frontend dev server port: '5173' for Vite, '3000' for CRA/Next"
    )
    websocket_library: Optional[str] = Field(
        default="",
        description="'native' if backend uses raw WebSocket (no SockJS), 'sockjs' if using SockJS+STOMP. Frontend MUST use matching client library."
    )

    @model_validator(mode="before")
    @classmethod
    def coerce_types_and_defaults(cls, values):
        """Coerce integer values and None to defaults/strings so Gemini's outputs don't fail."""
        defaults = {
            "api_base_url": "http://localhost:8000",
            "auth_token_field": "access",
            "auth_header_format": "Bearer {token}",
            "db_url_env_var": "DATABASE_URL",
            "frontend_port": "",
            "websocket_library": "",
        }
        if isinstance(values, dict):
            for field, default in defaults.items():
                val = values.get(field)
                if val is None:
                    values[field] = default
                elif not isinstance(val, str):
                    # Coerce int/other to str (e.g. port 5173 -> "5173")
                    values[field] = str(val)
        return values

class GeneratedFilesResponse(BaseModel):
    """Response schema for multiple generated files."""
    files: List[GeneratedFile]
    implementation_notes: Dict[str, str] = Field(
        default_factory=dict,
        description=(
            "Decisions made in this phase for downstream phases to consume. "
            "MANDATORY keys: 'packages_used' (comma-separated list of every external package imported, e.g. 'pinia,pinia-plugin-persistedstate,axios'), "
            "'port' (server port), 'db_handler' (e.g. 'pg', 'sqlalchemy'). "
            "The infrastructure phase reads 'packages_used' verbatim to build package.json / requirements.txt."
        )
    )
    interface_contracts: str = Field(
        default="",
        description="Markdown summary of the ACTUAL implementation shapes: Pydantic models (with all fields), specific DTOs, and full endpoint signatures. Downstream phases MUST use these exact shapes."
    )
    cross_layer_contracts: CrossLayerContractSchema = Field(
        default_factory=CrossLayerContractSchema,
        description="Typed synchronization facts for downstream phases. Populate ALL fields accurately."
    )

# for intent spec
class StackComponent(BaseModel):
    """Optional component of the technology stack."""
    framework: Optional[str] = None
    version: Optional[str] = None

class BackendComponent(BaseModel):
    """Required backend component of the technology stack."""
    framework: str = Field(..., description="Mandatory backend framework name")
    version: Optional[str] = None

class StackSchema(BaseModel):
    """Typed technology stack specification."""
    backend: BackendComponent = Field(..., description="Backend is mandatory")
    frontend: StackComponent = Field(default_factory=StackComponent)
    database: StackComponent = Field(default_factory=StackComponent)

    @model_validator(mode="before")
    @classmethod
    def coerce_strings_to_objects(cls, values):
        """Handle cases where Gemini returns a string instead of a dictionary for stack components."""
        if isinstance(values, dict):
            # Coerce backend
            if 'backend' in values and isinstance(values['backend'], str):
                values['backend'] = {"framework": values['backend']}
            
            # Coerce frontend
            if 'frontend' in values and isinstance(values['frontend'], str):
                values['frontend'] = {"framework": values['frontend']}
                
            # Coerce database
            if 'database' in values and isinstance(values['database'], str):
                values['database'] = {"framework": values['database']}
        return values

class DataEntity(BaseModel):
    """Represents a data model/entity."""
    name: str
    fields: List[str] = Field(default_factory=list)

class IntentSpecSchema(BaseModel):
    """
    Schema for Intent Specification - the single source of truth.
    User-editable, no folders/files/dependencies.
    """
    project_type: str = Field(
        ...,
        description="Detailed project type (e.g., 'url_shortener', 'todo_app', 'ecommerce_api')"
    )
    
    stack: StackSchema = Field(
        default_factory=StackSchema,
        description="Technology stack details including frameworks and versions."
    )
    
    api_type: Literal['rest', 'graphql', 'none'] = Field(
        default='rest',
        description="Type of API to generate for the backend"
    )
    features: List[str] = Field(
        default_factory=list,
        description="List of feature names like authentication, user_profiles, file_upload, etc - User can also add custom feature strings"
    )
    
    architecture: Literal['monolith', 'microservices'] = 'microservices'
    
    data_entities: List[DataEntity] = Field(
        default_factory=list,
        description="List of data models/entities specific to the project type"
    )
    
    auth_method: Literal['jwt', 'session', 'none'] = 'none'
    
    vague_intent: bool = Field(
        default=False,
        description="True if the user prompt was too vague and the system had to make significant assumptions"
    )
    
    explanation: str = Field(
        default="",
        description="Short explanation of why the prompt was considered vague and what assumptions were made"
    )
    
    creative_vision: str = Field(
        default="",
        description="Captures the unique 'soul' and dark-themed stylistic/functional nuances of the prompt (DevScaffold is DARK MODE ONLY). Used to guide downstream creative decisions."
    )

# for component plan
class Component(BaseModel):
    """Represents a single component in the plan."""
    id: str
    type: Literal['backend_module', 'frontend_component', 'data_model', 'middleware']
    folder: str = ""
    files: List[str] = Field(default_factory=list)
    responsibilities: List[str] = Field(default_factory=list)
    depends_on: List[str] = Field(default_factory=list)
    public_interfaces: List[str] = Field(default_factory=list)
    data_models: List[str] = Field(default_factory=list)

class ComponentPlanSchema(BaseModel):
    """Schema for Component Plan."""
    components: List[Component]

class DependencyEdge(BaseModel):
    """Represents a dependency edge in a graph."""
    from_component: str
    to_component: str

class CyclicDependencyError(Exception):
    """Raised when a cyclic dependency is detected."""
    pass


# Export only top-level schemas used externally
__all__ = [
    'IntentSpecSchema',
    'ComponentPlanSchema',
    'GeneratedFilesResponse',
    'DataEntity',
    'DependencyEdge',
    'CyclicDependencyError',
]
