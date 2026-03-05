import os
import sys
import django
from django.contrib.auth import get_user_model

# Setup Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'devscaffold.settings')
django.setup()

from pipeline.orchestrator import PipelineOrchestrator
from projects.models import Project

def test_pipeline():
    user = get_user_model().objects.get(username='adisrivastava027')
    project, _ = Project.objects.get_or_create(
        name="Test API Fixes", user=user,
        defaults={'prompt': "Build a simple user authentication API using FastAPI"}
    )
    
    print(f"Testing Project: {project.id}")
    success = PipelineOrchestrator(project).run()
    print("Result:", "SUCCESS" if success else f"FAILED: {project.status}")

if __name__ == '__main__':
    test_pipeline()
