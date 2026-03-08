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


from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
import tempfile
import shutil

def assemble_repository(project, intent_spec: IntentSpecSchema, generated_files: Dict[str, str], manifest=None, action_history: str = "") -> str:
    """
    Assembles the repository and uploads to storage (S3 or Local).
    Returns the storage path of the ZIP file.
    """
    project_name = f"project_{project.id}"
    backend_framework = intent_spec.stack.backend.framework if intent_spec.stack.backend else None

    # Use a temporary directory for local assembly before uploading
    with tempfile.TemporaryDirectory() as temp_dir_name:
        temp_dir = Path(temp_dir_name)
        
        # 1. Write files locally first (easier for zipping and __init__.py generation)
        for filepath, content in generated_files.items():
            normalized = filepath.lstrip('/').lstrip('\\').replace('\\', '/')
            file_path = temp_dir / normalized
            file_path.parent.mkdir(parents=True, exist_ok=True)
            
            if filepath.lower() == 'readme.md' and action_history:
                content += f"\n\n---\n\n## DevScaffold Pipeline Report\n\n```text\n{action_history}\n```\n"

            file_path.write_text(content, encoding='utf-8')
            
            # Python __init__.py generation
            if backend_framework and 'backend/' in filepath and file_path.suffix == '.py':
                parent = file_path.parent
                backend_base = temp_dir / 'backend'
                while parent.is_relative_to(backend_base):
                    init = parent / '__init__.py'
                    if not init.exists():
                        init.write_text('', encoding='utf-8')
                    parent = parent.parent

        # Add manifest.json
        if manifest:
            import json
            backend_dir = temp_dir / 'backend'
            if backend_dir.exists():
                (backend_dir / 'manifest.json').write_text(json.dumps(manifest.to_json(), indent=2))

        # 2. Create ZIP in the temp directory
        temp_zip_path = Path(temp_dir_name + "_zip.zip")
        create_zip(temp_dir, temp_zip_path)

        # 3. Upload/Move to Final Storage
        repo_storage_dir = f"projects/{project_name}"
        zip_storage_path = f"projects/{project_name}.zip"

        # Clear existing if local
        if hasattr(settings, 'STORAGE_PATH') and not settings.AWS_STORAGE_BUCKET_NAME:
            final_dir = settings.STORAGE_PATH / project_name
            if final_dir.exists():
                shutil.rmtree(final_dir)
            final_zip = settings.STORAGE_PATH / f"{project_name}.zip"
            if final_zip.exists():
                final_zip.unlink()

        # Upload files to storage (Individual files for browsing)
        for root, _, files in os.walk(temp_dir):
            for file in files:
                local_file = Path(root) / file
                rel_path = local_file.relative_to(temp_dir)
                storage_path = f"{repo_storage_dir}/{rel_path}".replace('\\', '/')
                with open(local_file, 'rb') as f:
                    default_storage.save(storage_path, ContentFile(f.read()))

        # Upload ZIP
        with open(temp_zip_path, 'rb') as f:
            default_storage.save(zip_storage_path, ContentFile(f.read()))

        # Cleanup temp zip
        if temp_zip_path.exists():
            temp_zip_path.unlink()

        # Update project model
        project.repo_directory = repo_storage_dir
        project.zip_file_path = zip_storage_path
        project.save()

        return zip_storage_path


def create_zip(source_dir: Path, zip_path: Path):
    """Create a ZIP file from the source directory."""
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(source_dir):
            for file in files:
                file_path = Path(root) / file
                arcname = file_path.relative_to(source_dir.parent)
                zipf.write(file_path, arcname)
