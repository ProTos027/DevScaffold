"""
Deterministic Repository Assembly - NO LLM INVOLVEMENT.
Creates folder structure, places files, generates configs, and creates ZIP.
"""
import os
import zipfile
from pathlib import Path
from typing import Dict
from django.conf import settings

from pipeline.schemas import IntentSpecSchema


def assemble_repository(project, intent_spec: IntentSpecSchema, generated_files: Dict[str, Dict[str, str]]) -> Path:
    """
    Deterministically assemble the repository from generated files.
    
    Args:
        project: Project model instance
        intent_spec: IntentSpecSchema
        generated_files: Dict mapping component_id to {filename: content}
    
    Returns:
        Path to the generated ZIP file
    """
    # Create project directory
    project_name = f"project_{project.id}"
    project_dir = settings.STORAGE_PATH / project_name
    project_dir.mkdir(parents=True, exist_ok=True)
    
    # Determine folder structure based on stack
    backend = intent_spec.stack.get('backend')
    frontend = intent_spec.stack.get('frontend')
    
    # Create backend structure
    if backend:
        backend_dir = project_dir / 'backend'
        backend_dir.mkdir(exist_ok=True)
        
        # Place framework boilerplate files first
        if '_boilerplate' in generated_files:
            for filepath, content in generated_files['_boilerplate'].items():
                # Handle nested paths like app/config.py
                file_path = backend_dir / filepath
                file_path.parent.mkdir(parents=True, exist_ok=True)
                file_path.write_text(content, encoding='utf-8')
        
        # Create layer-based structure for component files
        for comp_id, files in generated_files.items():
            if comp_id in ['_root', '_boilerplate']:
                continue
            
            for filepath, content in files.items():
                # If the filepath already looks structure-aware (e.g. "app/models/..." or "src/..."), trust it relative to backend_dir
                if '/' in filepath or '\\' in filepath:
                    file_path = backend_dir / filepath
                else:
                    # Deterministic mapping for simple filenames
                    if backend == 'fastapi':
                        if comp_id.endswith('_model') or any(entity.name.lower() in filepath.lower() for entity in intent_spec.data_entities):
                            file_path = backend_dir / 'app' / 'models' / filepath
                        else:
                            file_path = backend_dir / 'app' / 'routers' / filepath
                    elif backend == 'django':
                        file_path = backend_dir / 'apps' / comp_id / filepath
                    else:
                        file_path = backend_dir / comp_id / filepath
                
                # Ensure parent directory exists
                file_path.parent.mkdir(parents=True, exist_ok=True)
                
                # Add __init__.py if it's a new directory in Python projects
                if backend in ['fastapi', 'django', 'flask'] and file_path.suffix == '.py':
                    init_path = file_path.parent / '__init__.py'
                    if not init_path.exists():
                        init_path.write_text('', encoding='utf-8')
                
                file_path.write_text(content, encoding='utf-8')
    
    # Create frontend structure ONLY if frontend is specified and not null
    if frontend and frontend not in ['none', 'null', None]:
        frontend_dir = project_dir / 'frontend'
        frontend_dir.mkdir(exist_ok=True)
        
        # Place frontend component files
        for comp_id, files in generated_files.items():
            if comp_id == '_root':
                continue
            
            # Check if this is a frontend component
            # We can determine this by checking file extensions or component type
            has_frontend_files = any(fname.endswith('.jsx') or fname.endswith('.vue') for fname in files.keys())
            if has_frontend_files:
                comp_dir = frontend_dir / 'src' / 'components' / comp_id
                comp_dir.mkdir(parents=True, exist_ok=True)
                
                for filename, content in files.items():
                    file_path = comp_dir / filename
                    file_path.parent.mkdir(parents=True, exist_ok=True)
                    file_path.write_text(content, encoding='utf-8')
        
        # Generate package.json
        package_json = generate_package_json(frontend, project_name)
        (frontend_dir / 'package.json').parent.mkdir(parents=True, exist_ok=True)
        (frontend_dir / 'package.json').write_text(package_json, encoding='utf-8')
    
    # Add root files (README, .gitignore) - already included in boilerplate
    if '_root' in generated_files:
        for filename, content in generated_files['_root'].items():
            (project_dir / filename).write_text(content, encoding='utf-8')
    
    # Note: Startup scripts are now included in boilerplate generation
    
    # Create ZIP file
    zip_path = settings.STORAGE_PATH / f"{project_name}.zip"
    create_zip(project_dir, zip_path)
    
    # Save directory path
    project.repo_directory = str(project_dir)
    project.save()
    
    return zip_path


def generate_requirements(backend: str) -> str:
    """Generate Python requirements.txt based on backend choice."""
    if backend == 'django':
        return """Django==5.0.1
djangorestframework==3.14.0
django-cors-headers==4.3.1
python-decouple==3.8
"""
    elif backend == 'fastapi':
        return """fastapi==0.109.0
uvicorn==0.27.0
pydantic==2.5.3
python-decouple==3.8
"""
    return ""


def generate_package_json(frontend: str, project_name: str) -> str:
    """Generate package.json for frontend."""
    if frontend == 'react':
        return f"""{{
  "name": "{project_name}",
  "version": "1.0.0",
  "private": true,
  "dependencies": {{
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "react-router-dom": "^6.21.0",
    "axios": "^1.6.5"
  }},
  "scripts": {{
    "start": "react-scripts start",
    "build": "react-scripts build",
    "test": "react-scripts test"
  }}
}}
"""
    elif frontend == 'vue':
        return f"""{{
  "name": "{project_name}",
  "version": "1.0.0",
  "private": true,
  "dependencies": {{
    "vue": "^3.4.0",
    "vue-router": "^4.2.5",
    "axios": "^1.6.5"
  }},
  "scripts": {{
    "serve": "vue-cli-service serve",
    "build": "vue-cli-service build"
  }}
}}
"""
    return "{}"


def generate_startup_scripts(project_dir: Path, backend: str, frontend: str):
    """Generate startup scripts for the project."""
    
    # Bash script (Linux/Mac)
    bash_script = "#!/bin/bash\n\n"
    
    if backend:
        bash_script += """# Backend setup
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver &
cd ..

"""
    
    if frontend:
        bash_script += """# Frontend setup
cd frontend
npm install
npm start &
cd ..

"""
    
    bash_script += 'echo "DevScaffold project started!"\n'
    
    (project_dir / 'start.sh').write_text(bash_script, encoding='utf-8')
    (project_dir / 'start.sh').chmod(0o755)
    
    # PowerShell script (Windows)
    ps_script = ""
    
    if backend:
        ps_script += """# Backend setup
cd backend
python -m venv venv
.\\venv\\Scripts\\Activate.ps1
pip install -r requirements.txt
python manage.py migrate
Start-Process python -ArgumentList "manage.py","runserver"
cd ..

"""
    
    if frontend:
        ps_script += """# Frontend setup
cd frontend
npm install
Start-Process npm -ArgumentList "start"
cd ..

"""
    
    ps_script += 'Write-Host "DevScaffold project started!"\n'
    
    (project_dir / 'start.ps1').write_text(ps_script, encoding='utf-8')


def create_zip(source_dir: Path, zip_path: Path):
    """Create a ZIP file from the source directory."""
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(source_dir):
            for file in files:
                file_path = Path(root) / file
                arcname = file_path.relative_to(source_dir.parent)
                zipf.write(file_path, arcname)
