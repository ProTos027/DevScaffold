"""
Folder Contract Builder Agent - Generates an architectural blueprint for components.
"""
from google import genai
import json
from typing import List, Dict, Optional

from ..schemas import ComponentPlanSchema, FolderContractListSchema, IntentSpecSchema


FOLDER_CONTRACT_BUILDER_SYSTEM_PROMPT = """You are a software architect and directory structure expert.

Your job: Take a Component Plan and convert it into a concrete list of Folder Contracts.

CRITICAL DIRECTIVES:
1. CONSISTENCY: Ensure that if Component A depends on Component B, the folder paths and filenames are predicted accurately so they can import each other.
2. FRAMEWORK CONVENTIONS:
   - FastAPI: Use `app/models`, `app/routers`, `app/services` structure.
   - Spring Boot: Use `src/main/java/com/example/project/...` with `controller`, `service`, `model`, `repository` packages.
   - Django: Use `apps/<component_id>/...` with `models.py`, `views.py`, etc.
   - Express: Use `src/models`, `src/routes`, `src/controllers`.
3. FILE NAMES: Be explicit about file names (e.g., `user_model.py` instead of just `model`).
4. RESPONSIBILITIES: Pass down the specific responsibilities for EACH folder contract to guide the code generator.

Each Folder Contract must include:
- component_id: The ID from the plan.
- folder: The base folder for this component.
- files: List of specific files to be generated.
- responsibilities: What this specific folder/file set handles.
- interfaces: API endpoints or public methods it exposes.
- models_used: Names of data entities it interacts with.
"""


def build_folder_contracts(
    intent_spec: IntentSpecSchema,
    component_plan: ComponentPlanSchema,
    model_name: str,
    api_key: str
) -> FolderContractListSchema:
    """
    Use Google GenAI SDK to generate Folder Contracts from a Component Plan.
    """
    client = genai.Client(api_key=api_key)
    
    if not model_name.startswith("gemini-"):
        model_name = "gemini-2.5-flash"

    prompt = f"""
    Framework: {intent_spec.stack.get('backend')}
    Project Type: {intent_spec.project_type}
    Component Plan: {component_plan.model_dump_json(indent=2)}
    
    Generate a list of folder contracts that defines exactly where each component should live and what files it should contain.
    """

    try:
        response = client.models.generate_content(
            model=model_name,
            contents=prompt,
            config={
                "system_instruction": FOLDER_CONTRACT_BUILDER_SYSTEM_PROMPT,
                "response_mime_type": "application/json",
                "response_json_schema": FolderContractListSchema.model_json_schema(),
            },
        )
        
        content = response.candidates[0].content.parts[0].text
        data = json.loads(content)
        
        # Validate with Pydantic
        return FolderContractListSchema(**data)
        
    except Exception as e:
        from ..utils import format_gemini_error
        clean_msg = format_gemini_error(e)
        print(f"❌ FOLDER CONTRACT ERROR: {clean_msg}")
        # Build minimal contracts manually if LLM fails
        contracts = []
        for comp in component_plan.components:
            contracts.append({
                "component_id": comp.id,
                "folder": f"app/{comp.id}",
                "files": ["__init__.py", f"{comp.id}.py"],
                "responsibilities": comp.responsibilities,
                "dependencies": comp.depends_on,
                "interfaces": comp.public_interfaces,
                "models_used": comp.data_models
            })
        return FolderContractListSchema(contracts=contracts)
