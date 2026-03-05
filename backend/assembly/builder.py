"""
Deterministic Repository Assembly - NO LLM INVOLVEMENT.
Creates folder structure, places files, generates configs, and creates ZIP.
"""
import os
import zipfile
from pathlib import Path
from typing import Dict
from django.conf import settings

from core.logger import get_logger
from pipeline.schemas import IntentSpecSchema

logger = get_logger(__name__)


# Default framework versions — used when user doesn't specify a version
DEFAULT_VERSIONS = {
    'django': {
        'framework': '5.0.1',
        'deps': {
            'djangorestframework': '3.14.0',
            'django-cors-headers': '4.3.1',
            'python-decouple': '3.8',
            'djangorestframework-simplejwt': '5.3.1',
            'Pillow': '10.2.0',
        }
    },
    'fastapi': {
        'framework': '0.109.0',
        'deps': {
            'uvicorn': '0.27.0',
            'pydantic': '2.5.3',
            'pydantic-settings': '2.1.0',
            'python-jose': '3.3.0',
            'passlib': '1.7.4',
            'python-multipart': '0.0.6',
            'sqlalchemy': '2.0.25',
            'python-decouple': '3.8',
        }
    },
    'flask': {
        'framework': '3.0.0',
        'deps': {
            'flask-cors': '4.0.0',
            'flask-sqlalchemy': '3.1.1',
            'flask-jwt-extended': '4.6.0',
            'python-decouple': '3.8',
        }
    },
    'react': {
        'framework': '18.2.0',
        'deps': {
            'react-dom': '18.2.0',
            'react-router-dom': '6.21.0',
            'axios': '1.6.5',
        }
    },
    'vue': {
        'framework': '3.4.0',
        'deps': {
            'vue-router': '4.2.5',
            'pinia': '2.1.7',
            'axios': '1.6.5',
        }
    },
    'express': {
        'framework': '4.18.2',
        'deps': {
            'cors': '2.8.5',
            'dotenv': '16.3.1',
            'jsonwebtoken': '9.0.2',
            'bcryptjs': '2.4.3',
        }
    },
}

# Available versions for frontend dropdowns
AVAILABLE_VERSIONS = {
    'django': ['4.2', '5.0', '5.0.1', '5.1'],
    'fastapi': ['0.100.0', '0.109.0', '0.115.0'],
    'flask': ['2.3.0', '3.0.0'],
    'express': ['4.18.2', '4.19.0', '5.0.0'],
    'springboot': ['3.1.0', '3.2.0', '3.3.0'],
    'react': ['17.0.2', '18.2.0', '18.3.0', '19.0.0'],
    'vue': ['3.3.0', '3.4.0', '3.5.0'],
    'nextjs': ['13.5.0', '14.0.0', '15.0.0'],
}


def assemble_repository(project, intent_spec: IntentSpecSchema, generated_files: Dict[str, str], manifest=None, action_history: str = "") -> Path:
    """
    Verbatim Repository Assembly - Deterministic and Simple.
    Writes every file to the exact path provided by the Generation Engine.
    """
    # Create project directory
    project_name = f"project_{project.id}"
    project_dir = settings.STORAGE_PATH / project_name
    if project_dir.exists():
        import shutil
        shutil.rmtree(project_dir)
    project_dir.mkdir(parents=True, exist_ok=True)
    
    backend = intent_spec.stack.backend

    # 1. Validate against Manifest Layout (Non-blocking)
    if manifest and manifest.directory_layout:
        expected_paths = set()
        for contract in manifest.directory_layout:
            folder = contract.get('folder', '').strip('/')
            for filename in contract.get('files', []):
                # Reconstruct the full path as expected in generated_files keys
                full_path = f"{folder}/{filename}" if folder else filename
                expected_paths.add(full_path)
        
        actual_paths = set(generated_files.keys())
        missing = expected_paths - actual_paths
        extra = actual_paths - expected_paths
        
        if missing:
            logger.warning(f"ASSEMBLY WARNING: {len(missing)} files missing from Manifest layout: {list(missing)[:5]}...")
        if extra:
            logger.info(f"ASSEMBLY INFO: {len(extra)} files generated outside of Manifest layout: {list(extra)[:5]}...")

    # 2. Process all files verbatim
    for filepath, content in generated_files.items():
        # Path normalization: strip leading slashes to prevent pathlib treating path as absolute
        # e.g. '/README.md' would resolve to 'C:\README.md' without this
        normalized = filepath.lstrip('/').lstrip('\\').replace('\\', '/')
        file_path = project_dir / normalized
        
        # Ensure parent directory exists
        file_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Inject Action Logger summary into README.md
        if filepath.lower() == 'readme.md' and action_history:
            content += f"\n\n---\n\n## DevScaffold Pipeline Report\n\n```text\n{action_history}\n```\n"

        # Write the file
        file_path.write_text(content, encoding='utf-8')
        
        # Add __init__.py for Python backend directories (Ensures valid packages)
        if backend and 'backend/' in filepath and file_path.suffix == '.py':
            backend_base = project_dir / 'backend'
            parent = file_path.parent
            while parent != backend_base and parent != project_dir:
                init = parent / '__init__.py'
                if not init.exists():
                    init.write_text('', encoding='utf-8')
                parent = parent.parent

    # 2. Save Physical Manifest (for RAG or debugging)
    if manifest:
        import json
        backend_dir = project_dir / 'backend'
        if backend_dir.exists():
            manifest_path = backend_dir / 'manifest.json'
            manifest_path.write_text(json.dumps(manifest.to_json(), indent=2), encoding='utf-8')
    
    # 3. Create ZIP file
    zip_path = settings.STORAGE_PATH / f"{project_name}.zip"
    create_zip(project_dir, zip_path)
    
    # Save project metadata
    project.repo_directory = str(project_dir)
    project.save()
    
    return zip_path


def create_zip(source_dir: Path, zip_path: Path):
    """Create a ZIP file from the source directory."""
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(source_dir):
            for file in files:
                file_path = Path(root) / file
                arcname = file_path.relative_to(source_dir.parent)
                zipf.write(file_path, arcname)
