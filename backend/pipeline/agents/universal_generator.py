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
        gemini_model = "gemini-2.5-flash"
        
    backend = (intent_spec.stack.get('backend')).lower()
    backend_version = intent_spec.stack.get('backend_version', '')
    database = intent_spec.stack.get('database', 'sqlite')
    frontend = intent_spec.stack.get('frontend')
    frontend_version = intent_spec.stack.get('frontend_version', '')
    
    version_ctx = f" v{backend_version}" if backend_version else ""
    fe_version_ctx = f" v{frontend_version}" if frontend_version else ""
    
    system_instruction = f"""You are a software project scaffolding expert.
Generate a complete, production-ready {backend}{version_ctx} project boilerplate.

Requirements:
- Follow {backend}{version_ctx} best practices and conventions.
- Create proper directory structure and necessary configuration files.
- Include database setup if needed.
- Add basic error handling.
- **CRITICAL: Startup scripts (start.ps1 for Windows, start.sh for Linux/Mac)**
   - These must run the correct command for {backend}.
   - Include environment setup (venv activation, npm install, etc.).
{f'- IMPORTANT: Use {backend} version {backend_version} compatible syntax and dependencies.' if backend_version else ''}
"""

    components_info = [
        {'id': comp.id, 'type': comp.type, 'responsibilities': comp.responsibilities}
        for comp in component_plan.components
    ]
    
    prompt = f"""
Framework: {backend}{version_ctx}
Project Type: {intent_spec.project_type}
Complexity: {intent_spec.complexity}
Database: {database}
Features: {intent_spec.features}
Components: {components_info}
{f'Frontend: {frontend}{fe_version_ctx}' if frontend else ''}

Generate:
1. Entry point file.
2. Configuration files.
3. Database connection setup.
4. Directory structure files (package.json, pom.xml, etc.).
5. .gitignore and README.md.
6. Dependency files (with correct versions).
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


def sanitize_generated_content(content: str) -> str:
    """
    Sanitize generated content to fix common LLM formatting bugs.
    Specifically targets the issue where '\n' becomes 'n'.
    """
    if not content:
        return content
        
    # Fix the 'n-newline' bug in shell scripts
    if content.startswith('#!') or 'echo \"' in content:
        # Heuristic: if we see common script patterns followed by 'n' where a newline should be
        content = content.replace('bashnn', 'bash\n\n')
        content = content.replace('pipen', 'pipe\n')
        content = content.replace('\"nn', '\"\n\n')
        content = content.replace('nelsen', 'nelse\n')
        content = content.replace('nfin', 'nfi\n')
        content = content.replace('ncfign', 'nconfig\n')
        
        # General fix for 'n' followed by common keywords if the file looks mangled
        if '#!/bin/bash' in content or '#!/bin/sh' in content:
            import re
            
            # Step 1: Replace double 'n' which nearly always indicates double newline in these scripts
            content = content.replace('nn', '\n\n')
            
            # Step 2: Replace single 'n' followed by common keywords/patterns
            patterns = [
                (r'echo \"', '\necho \"'),
                (r'set -', '\nset -'),
                (r'export ', '\nexport '),
                (r'if \[', '\nif ['),
                (r'else', '\nelse'),
                (r'fi', '\nfi'),
                (r'done', '\ndone'),
                (r'cd ', '\ncd '),
                (r'python ', '\npython '),
                (r'source ', '\nsource '),
                (r'pip ', '\npip '),
                (r'VENV_DIR=', '\nVENV_DIR='),
                (r'REQUIREMENTS_FILE=', '\nREQUIREMENTS_FILE='),
            ]
            for pat, rep in patterns:
                # Use lookahead to replace 'n' only if it precedes the pattern
                content = re.sub(f'n(?={pat})', '\n', content)
            
            # Step 3: Cleanup common script ending patterns
            content = content.replace('thenn', 'then\n')
            content = content.replace('elsen', 'else\n')
            content = content.replace('fin', 'fi\n')
            content = content.replace('donen', 'done\n')
            
    return content


def universal_generate(
    intent_spec,
    component_plan,
    project_id: int,
    gemini_model: str,
    api_key: str
) -> Dict[str, str]:
    """Universal generation function - Pure LLM based."""
    files = generate_custom_boilerplate(intent_spec, component_plan, gemini_model, api_key)
    return {path: sanitize_generated_content(content) for path, content in files.items()}
