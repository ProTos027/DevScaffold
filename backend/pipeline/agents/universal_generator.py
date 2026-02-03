"""
Universal Generator - Pure LLM-based boilerplate generation.
"""
from google import genai
import json
from typing import Dict, List, Optional

from ..schemas import GeneratedFilesResponse


def generate_custom_boilerplate(
    intent_spec,
    component_plan,
    gemini_model: str,
    api_key: str
) -> Dict[str, str]:
    """
    Generate custom boilerplate using Google GenAI SDK.
    """
    client = genai.Client(api_key=api_key)
    
    if not gemini_model.startswith("gemini-"):
        gemini_model = "gemini-1.5-flash"
        
    backend = (intent_spec.stack.get('backend')).lower()
    database = intent_spec.stack.get('database', 'sqlite')
    
    system_instruction = f"""You are a software project scaffolding expert.
Generate a complete, production-ready {backend} project boilerplate.

Requirements:
- Follow {backend} best practices and conventions.
- Create proper directory structure and necessary configuration files.
- Include database setup if needed.
- Add basic error handling.
- **CRITICAL: Startup scripts (start.ps1 for Windows, start.sh for Linux/Mac)**
   - These must run the correct command for {backend}.
   - Include environment setup (venv activation, npm install, etc.).
"""

    components_info = [
        {'id': comp.id, 'type': comp.type, 'responsibilities': comp.responsibilities}
        for comp in component_plan.components
    ]
    
    prompt = f"""
Framework: {backend}
Project Type: {intent_spec.project_type}
Complexity: {intent_spec.complexity}
Database: {database}
Features: {intent_spec.features}
Components: {components_info}

Generate:
1. Entry point file.
2. Configuration files.
3. Database connection setup.
4. Directory structure files (package.json, pom.xml, etc.).
5. .gitignore and README.md.
6. Dependency files.
7. Startup scripts (start.sh, start.ps1).
"""

    response = client.models.generate_content(
        model=gemini_model,
        contents=prompt,
        config={
            "system_instruction": system_instruction,
            "response_mime_type": "application/json",
            "response_json_schema": GeneratedFilesResponse.model_json_schema(),
        }
    )
    
    data = json.loads(response.candidates[0].content.parts[0].text)
    return {f['path']: f['content'] for f in data.get('files', [])}


def universal_generate(
    intent_spec,
    component_plan,
    project_id: int,
    gemini_model: str,
    api_key: str
) -> Dict[str, str]:
    """Universal generation function - Pure LLM based."""
    return generate_custom_boilerplate(intent_spec, component_plan, gemini_model, api_key)
