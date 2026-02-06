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
    api_key: str
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
    for comp_id in build_order:
        comp = next((c for c in component_plan.components if c.id == comp_id), None)
        contract = next((c for c in folder_contracts.contracts if c.component_id == comp_id), None)
        if not comp or not contract:
            continue
        
        files = {}
        if comp.type == 'data_model':
            files.update(generate_data_model(comp, contract, intent_spec, client, model_name))
        elif comp.type == 'backend_module':
            files.update(generate_backend_module(comp, contract, intent_spec, client, model_name))
        elif comp.type == 'frontend_component':
            files.update(generate_frontend_component(comp, contract, intent_spec, client, model_name))
        
        generated[comp_id] = files
    
    # Add root files
    generated['_root'] = generate_root_files(intent_spec)
    
    return generated


def generate_data_model(comp: Component, contract, intent_spec: IntentSpecSchema, client, model_name: str) -> Dict[str, str]:
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

    system_instruction = f"""You are a senior software engineer. Generate data model code.
Framework: {backend}
Target Folder: {contract.folder}
Expected Files: {contract.files}

CRITICAL REQUIREMENTS:
1. Generate ACTUAL code for the files defined in the Folder Contract.
2. Responsibilities: {contract.responsibilities}
3. Interfaces to implement: {contract.interfaces}
4. For Java (Spring Boot): Use JPA annotations.
5. NO PLACEHOLDERS.
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


def generate_backend_module(comp: Component, contract, intent_spec: IntentSpecSchema, client, model_name: str) -> Dict[str, str]:
    """Generate backend module files using Google GenAI SDK and Folder Contract."""
    backend = (intent_spec.stack.get('backend')).lower()
    
    system_instruction = f"""You are a senior backend engineer. Implement business logic.
Framework: {backend}
Target Folder: {contract.folder}
Expected Files: {contract.files}

CRITICAL REQUIREMENTS:
1. Implement ACTUAL logic for the files defined in the Folder Contract.
2. Responsibilities: {contract.responsibilities}
3. Interfaces/Endpoints: {contract.interfaces}
4. Models to use: {contract.models_used}
5. Ensure the module is functional and includes necessary imports from other components.
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


def generate_frontend_component(comp: Component, contract, intent_spec: IntentSpecSchema, client, model_name: str) -> Dict[str, str]:
    """Generate frontend component files using Folder Contract."""
    frontend = intent_spec.stack.get('frontend', 'react')
    comp_name = comp.id.replace('_', ' ').title().replace(' ', '')
    
    system_instruction = f"""You are a senior frontend engineer. Generate a {frontend} component.
Target Folder: {contract.folder}
Expected Files: {contract.files}

CRITICAL REQUIREMENTS:
1. Implement the UI for the files defined in the Folder Contract.
2. Responsibilities: {contract.responsibilities}
3. Use modern patterns (Hooks for React/Vue).
4. NO PLACEHOLDERS.
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
