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


from django.core.files.storage import default_storage

def cleanup_expired_repositories():
    """
    Delete expired repositories based on deletion_scheduled_at.
    """
    from projects.models import Project
    
    now = timezone.now()
    expired_projects = Project.objects.filter(
        deletion_scheduled_at__lte=now,
        status='completed'
    )
    
    for project in expired_projects:
        # 1. Delete ZIP file
        if project.zip_file_path:
            if default_storage.exists(project.zip_file_path):
                default_storage.delete(project.zip_file_path)
        
        # 2. Delete repository directory (Iterate and delete for S3)
        if project.repo_directory:
            try:
                # S3 doesn't have directories, but we "list and delete" by prefix
                # Django storage listdir returns (dirs, files)
                def delete_recursive(prefix):
                    dirs, files = default_storage.listdir(prefix)
                    for f in files:
                        default_storage.delete(f"{prefix}/{f}")
                    for d in dirs:
                        delete_recursive(f"{prefix}/{d}")
                    # Note: S3 empty prefixes disappear automatically
                
                delete_recursive(project.repo_directory)
            except Exception as e:
                import logging
                logging.error(f"Cleanup error for {project.id}: {e}")
        
        # Update project
        project.zip_file_path = None
        project.repo_directory = None
        project.save()
    
    return expired_projects.count()
