"""
Code Generator - Uses Google GenAI SDK to generate actual implementation files.
"""
from typing import Dict, List, Optional
from google import genai
import json

from .. import schemas
from ..schemas import ComponentPlanSchema, IntentSpecSchema, Component, DataEntity, GeneratedFilesResponse, FolderContractListSchema


def generate_files_with_gemini(
    intent_spec: IntentSpecSchema,
    component_plan: ComponentPlanSchema,
    folder_contracts: FolderContractListSchema,
    build_order: List[str],
    model_name: str,
    api_key: str,
    action_logger=None,
    rag_service=None
) -> Dict[str, Dict[str, str]]:
    """
    Generate actual implementation files using Google GenAI SDK.
    """
    generated = {}
    
    # Initialize Google GenAI Client
    client = genai.Client(api_key=api_key)
    
    if not model_name.startswith("gemini-"):
        model_name = "gemini-2.5-flash"
    
    # UNIVERSAL GENERATION: Generate framework boilerplate
    from .universal_generator import universal_generate
    
    try:
        boilerplate_files = universal_generate(
            intent_spec,
            component_plan,
            project_id=hash(str(intent_spec)) % 10000,
            gemini_model=model_name,
            api_key=api_key
        )
        generated['_boilerplate'] = boilerplate_files
    except Exception as e:
        print(f"❌ Universal generation failed: {e}")
        generated['_boilerplate'] = {
            'README.md': f"# {intent_spec.project_type.title()} Project\n\nBoilerplate generation failed: {e}",
            '.gitignore': '*.pyc\n__pycache__/\nnode_modules/\n'
        }
    
    # Generate component files
    # Get pipeline action summary for context injection
    action_summary = action_logger.get_summary() if action_logger else ""
    
    for comp_id in build_order:
        comp = next((c for c in component_plan.components if c.id == comp_id), None)
        contract = next((c for c in folder_contracts.contracts if c.component_id == comp_id), None)
        if not comp or not contract:
            continue
        
        files = {}
        
        # RAG: Retrieve framework-specific context for this component
        rag_context = ""
        if rag_service:
            try:
                query = f"{comp.type} {comp.id} {' '.join(comp.responsibilities)}"
                rag_context = rag_service.retrieve(query, top_k=3)
            except Exception as e:
                print(f"⚠️ RAG retrieval failed for {comp_id} (non-fatal): {e}")
        
        if comp.type == 'data_model':
            files.update(generate_data_model(comp, contract, intent_spec, client, model_name, action_summary, rag_context))
        elif comp.type == 'backend_module':
            files.update(generate_backend_module(comp, contract, intent_spec, client, model_name, action_summary, rag_context))
        elif comp.type == 'frontend_component':
            files.update(generate_frontend_component(comp, contract, intent_spec, client, model_name, action_summary, rag_context))
        
        generated[comp_id] = files
        
        # Log each generated component
        if action_logger:
            action_logger.log('code_generation', 'code_generator', f'generated_{comp.type}', {
                'component_id': comp_id,
                'file_count': len(files),
                'files': list(files.keys()),
                'rag_used': bool(rag_context),
            })
    
    # Add root files
    generated['_root'] = generate_root_files(intent_spec)
    
    return generated


def generate_data_model(comp: Component, contract, intent_spec: IntentSpecSchema, client, model_name: str, action_summary: str = "", rag_context: str = "") -> Dict[str, str]:
    """Generate data model files using Google GenAI SDK and Folder Contract."""
    backend = (intent_spec.stack.get('backend')).lower()
    model_entity_name = comp.data_models[0] if comp.data_models else comp.id.title().replace('_', '')
    entity = next((e for e in intent_spec.data_entities if e.name == model_entity_name), None)
    
    lang_info = {
        'django': ('Python', 'Django models.py'),
        'fastapi': ('Python', 'SQLAlchemy / Pydantic'),
        'springboot': ('Java', 'JPA/Hibernate Entities + DTOs'),
        'express': ('JavaScript', 'Sequelize/Mongoose models'),
        'flask': ('Python', 'SQLAlchemy'),
        'rails': ('Ruby', 'ActiveRecord models')
    }.get(backend, ('any', 'standard patterns'))

    backend_version = intent_spec.stack.get('backend_version', '')
    version_ctx = f" v{backend_version}" if backend_version else ""

    # Build context strings outside f-string (backslashes not allowed in f-string expressions)
    pipeline_ctx = f"PIPELINE CONTEXT (previous agent decisions):\n{action_summary}" if action_summary else ""
    rag_ctx = rag_context if rag_context else ""

    system_instruction = f"""You are a senior software engineer. Generate data model code.
Framework: {backend}{version_ctx}
Target Folder: {contract.folder}
Expected Files: {contract.files}

CRITICAL REQUIREMENTS:
1. Generate ACTUAL code for the files defined in the Folder Contract.
2. Responsibilities: {contract.responsibilities}
3. Interfaces to implement: {contract.interfaces}
4. For Java (Spring Boot): Use JPA annotations.
5. NO PLACEHOLDERS.
{f'6. IMPORTANT: Generate code compatible with {backend} version {backend_version}.' if backend_version else ''}
{pipeline_ctx}
{rag_ctx}
"""

    prompt = f"Model Name: {model_entity_name}\nFields: {entity.fields if entity else 'id, created_at, updated_at'}"

    response = client.models.generate_content(
        model=model_name,
        contents=prompt,
        config={
            "system_instruction": system_instruction,
            "response_mime_type": "application/json",
            "response_json_schema": GeneratedFilesResponse.model_json_schema(),
        }
    )
    
    data = json.loads(response.candidates[0].content.parts[0].text)
    # Ensure paths are prefixed with the contract folder if they aren't absolute within the project
    return {f['path'] if f['path'].startswith(contract.folder) else f"{contract.folder}/{f['path']}".replace('//', '/'): f['content'] for f in data.get('files', [])}


def generate_backend_module(comp: Component, contract, intent_spec: IntentSpecSchema, client, model_name: str, action_summary: str = "", rag_context: str = "") -> Dict[str, str]:
    """Generate backend module files using Google GenAI SDK and Folder Contract."""
    backend = (intent_spec.stack.get('backend')).lower()
    backend_version = intent_spec.stack.get('backend_version', '')
    version_ctx = f" v{backend_version}" if backend_version else ""
    
    # Build context strings outside f-string
    pipeline_ctx = f"PIPELINE CONTEXT (previous agent decisions):\n{action_summary}" if action_summary else ""
    rag_ctx = rag_context if rag_context else ""

    system_instruction = f"""You are a senior backend engineer. Implement business logic.
Framework: {backend}{version_ctx}
Target Folder: {contract.folder}
Expected Files: {contract.files}

CRITICAL REQUIREMENTS:
1. Implement ACTUAL logic for the files defined in the Folder Contract.
2. Responsibilities: {contract.responsibilities}
3. Interfaces/Endpoints: {contract.interfaces}
4. Models to use: {contract.models_used}
5. Ensure the module is functional and includes necessary imports from other components.
{f'6. IMPORTANT: Generate code compatible with {backend} version {backend_version}.' if backend_version else ''}
{pipeline_ctx}
{rag_ctx}
"""

    prompt = f"Component ID: {comp.id}\nPublic Interfaces: {', '.join(comp.public_interfaces)}\nData Models: {', '.join(comp.data_models)}"

    response = client.models.generate_content(
        model=model_name,
        contents=prompt,
        config={
            "system_instruction": system_instruction,
            "response_mime_type": "application/json",
            "response_json_schema": GeneratedFilesResponse.model_json_schema(),
        }
    )
    
    data = json.loads(response.candidates[0].content.parts[0].text)
    return {f['path'] if f['path'].startswith(contract.folder) else f"{contract.folder}/{f['path']}".replace('//', '/'): f['content'] for f in data.get('files', [])}


def generate_frontend_component(comp: Component, contract, intent_spec: IntentSpecSchema, client, model_name: str, action_summary: str = "", rag_context: str = "") -> Dict[str, str]:
    """Generate frontend component files using Folder Contract."""
    frontend = intent_spec.stack.get('frontend', 'react')
    frontend_version = intent_spec.stack.get('frontend_version', '')
    version_ctx = f" v{frontend_version}" if frontend_version else ""
    comp_name = comp.id.replace('_', ' ').title().replace(' ', '')
    
    # Build context strings outside f-string
    pipeline_ctx = f"PIPELINE CONTEXT (previous agent decisions):\n{action_summary}" if action_summary else ""
    rag_ctx = rag_context if rag_context else ""

    system_instruction = f"""You are a senior frontend engineer. Generate a {frontend}{version_ctx} component.
Target Folder: {contract.folder}
Expected Files: {contract.files}

CRITICAL REQUIREMENTS:
1. Implement the UI for the files defined in the Folder Contract.
2. Responsibilities: {contract.responsibilities}
3. Use modern patterns (Hooks for React/Vue).
4. NO PLACEHOLDERS.
{f'5. IMPORTANT: Generate code compatible with {frontend} version {frontend_version}.' if frontend_version else ''}
{pipeline_ctx}
{rag_ctx}
"""

    prompt = f"Component Name: {comp_name}\nResponsibilities: {', '.join(comp.responsibilities)}"

    response = client.models.generate_content(
        model=model_name,
        contents=prompt,
        config={
            "system_instruction": system_instruction,
            "response_mime_type": "application/json",
            "response_json_schema": GeneratedFilesResponse.model_json_schema(),
        }
    )
    
    data = json.loads(response.candidates[0].content.parts[0].text)
    return {f['path'] if f['path'].startswith(contract.folder) else f"{contract.folder}/{f['path']}".replace('//', '/'): f['content'] for f in data.get('files', [])}


def generate_root_files(intent_spec: IntentSpecSchema) -> Dict[str, str]:
    """Generate root project files (README, .gitignore)."""
    backend = intent_spec.stack.get('backend', 'None')
    frontend = intent_spec.stack.get('frontend', 'None')
    database = intent_spec.stack.get('database', 'sqlite')
    
    readme = f"""# {intent_spec.project_type.replace('_', ' ').title()} Project

Generated by DevScaffold

## Stack
- **Frontend**: {frontend}
- **Backend**: {backend}
- **Database**: {database}

## Setup
Run the start.sh or start.ps1 scripts in the project root.
"""
    return {
        'README.md': readme,
        '.gitignore': 'node_modules/\nvenv/\n__pycache__/\n*.pyc\n*.sqlite3\n.env\n'
    }
