"""
File storage manager - handles repository storage and cleanup.
"""
from pathlib import Path
from django.conf import settings
from django.utils import timezone
import shutil


def get_storage_path() -> Path:
    """Get the storage path for generated repositories."""
    return settings.STORAGE_PATH


def cleanup_expired_repositories():
    """
    Delete expired repositories based on deletion_scheduled_at.
    This should be run as a periodic Celery task or management command.
    """
    from projects.models import Project
    
    now = timezone.now()
    expired_projects = Project.objects.filter(
        deletion_scheduled_at__lte=now,
        status='completed'
    )
    
    for project in expired_projects:
        # Delete ZIP file
        if project.zip_file_path:
            zip_path = Path(project.zip_file_path)
            if zip_path.exists():
                zip_path.unlink()
        
        # Delete repository directory
        if project.repo_directory:
            repo_dir = Path(project.repo_directory)
            if repo_dir.exists():
                shutil.rmtree(repo_dir)
        
        # Update project
        project.zip_file_path = None
        project.repo_directory = None
        project.save()
    
    return expired_projects.count()
