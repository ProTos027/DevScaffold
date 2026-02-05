"""
Pydantic models/schemas for the DevScaffold pipeline.
These define the strict structure for Intent Specs, Component Plans, etc.
"""
from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Literal


class GeneratedFile(BaseModel):
    """Schema for a single generated file."""
    path: str
    content: str
    language: str


class GeneratedFilesResponse(BaseModel):
    """Response schema for multiple generated files."""
    files: List[GeneratedFile]


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
    complexity: Literal['minimal', 'standard', 'full'] = 'standard'
    
    stack: Dict[str, Optional[str]] = Field(
        default_factory=dict,
        description="Technology stack: backend (fastapi|django|springboot|express|flask|rails), frontend (react|vue|nextjs|null), database (postgres|mysql|sqlite|mongodb|null)"
    )
    
    features: List[str] = Field(
        default_factory=list,
        description="List of feature names like authentication, url_shortening, blog_posts, etc - ONLY features user explicitly requested"
    )
    
    architecture: Dict[str, str] = Field(
        default_factory=dict,
        description="Architecture style (monolith|microservices) and API type (rest|graphql)"
    )
    
    data_entities: List[DataEntity] = Field(
        default_factory=list,
        description="List of data models/entities specific to the project type"
    )
    
    constraints: Dict[str, Optional[str]] = Field(
        default_factory=dict,
        description="Additional constraints like auth_method (jwt|session|null)"
    )
    
    vague_intent: bool = Field(
        default=False,
        description="True if the user prompt was too vague and the system had to make significant assumptions"
    )
    
    explanation: str = Field(
        default="",
        description="Short explanation of why the prompt was considered vague and what assumptions were made"
    )


class Component(BaseModel):
    """Represents a single component in the plan."""
    id: str
    type: Literal['backend_module', 'frontend_component', 'data_model', 'middleware']
    responsibilities: List[str] = Field(default_factory=list)
    depends_on: List[str] = Field(default_factory=list)
    public_interfaces: List[str] = Field(default_factory=list)
    data_models: List[str] = Field(default_factory=list)


class ComponentPlanSchema(BaseModel):
    """Schema for Component Plan."""
    components: List[Component]


class DependencyEdge(BaseModel):
    """Represents a dependency edge."""
    from_component: str
    to_component: str


class DependencyGraphSchema(BaseModel):
    """Schema for Dependency Graph."""
    nodes: List[str]
    edges: List[DependencyEdge]


class FolderContractSchema(BaseModel):
    """Schema for Folder Contract - Architectural Blueprint for high consistency."""
    component_id: str
    folder: str  # Initial proposed folder
    files: List[str]  # List of filenames expected (e.g., ["models.py", "serializers.py"])
    responsibilities: List[str] = Field(default_factory=list)
    dependencies: List[str] = Field(default_factory=list)
    interfaces: List[str] = Field(default_factory=list)
    models_used: List[str] = Field(default_factory=list)


class FolderContractListSchema(BaseModel):
    """List of all folder contracts for a project."""
    contracts: List[FolderContractSchema]


# Export all schemas
__all__ = [
    'DataEntity',
    'IntentSpecSchema',
    'Component',
    'ComponentPlanSchema',
    'DependencyEdge',
    'DependencyGraphSchema',
    'FolderContractSchema',
    'FolderContractListSchema',
    'GeneratedFile',
    'GeneratedFilesResponse',
]
