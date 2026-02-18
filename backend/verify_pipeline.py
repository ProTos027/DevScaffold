"""
End-to-end pipeline verification test.
Creates a project, runs the full pipeline, and checks all features.
"""
import os, sys, traceback
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'devscaffold.settings')

# Redirect output to log file to avoid Windows encoding issues
log_file = open('verify_output.log', 'w', encoding='utf-8')
sys.stdout = log_file
sys.stderr = log_file

import django
django.setup()

from django.contrib.auth import get_user_model
from accounts.models import APIKey
from projects.models import Project, PipelineActionLog
from pipeline.orchestrator import PipelineOrchestrator

User = get_user_model()

# Get user with an API key
api_key_obj = APIKey.objects.filter(provider='gemini').exclude(api_key_encrypted='').first()
if not api_key_obj:
    print("ERROR: No Gemini API key found")
    sys.exit(1)
user = api_key_obj.user

print(f"=== Pipeline Verification ===")
print(f"User: {user.email}")
print(f"API Key: {'SET' if api_key_obj else 'MISSING'}")

# Create a test project with version info
project = Project.objects.create(
    user=user,
    name="Pipeline Test - Todo App",
    prompt="Build a simple todo list app with Django 4.2 backend and React 18 frontend with PostgreSQL database",
    model_provider='gemini',
    gemini_model='gemini-2.5-flash',
    status='pending'
)

# Link API key
if api_key_obj:
    project.gemini_api_key = api_key_obj
    project.save()

print(f"Project ID: {project.id}")
print(f"Prompt: {project.prompt}")
print()

# Run pipeline
print("--- Stage 1: Running pipeline (spec build only) ---")
try:
    orchestrator = PipelineOrchestrator(project)
    result = orchestrator.run()
    print(f"Result: {result}")
    print(f"Status: {project.status}")
    
    if project.status == 'review_required':
        print("  -> Spec generated, paused for review (expected)")
        
        # Check the intent spec
        project.refresh_from_db()
        spec = project.intent_spec
        print(f"  Project type: {spec.project_type}")
        print(f"  Stack: {spec.stack}")
        print(f"  Backend version: {spec.stack.get('backend_version', 'NOT SET')}")
        print(f"  Frontend version: {spec.stack.get('frontend_version', 'NOT SET')}")
        print(f"  Features: {spec.features}")
        print(f"  Data entities: {[e['name'] for e in spec.data_entities]}")
        
        # Check action logs from spec building
        logs = PipelineActionLog.objects.filter(project=project)
        print(f"\n  Action logs: {logs.count()}")
        for log in logs:
            print(f"    [{log.stage}] {log.agent}: {log.action}")
            print(f"      Details: {log.details}")
        
        # Now confirm spec and run full pipeline
        print("\n--- Stage 2: Confirming spec and running full pipeline ---")
        project.spec_confirmed = True
        project.save()
        
        result2 = orchestrator.run()
        project.refresh_from_db()
        print(f"Result: {result2}")
        print(f"Status: {project.status}")
        
        if project.status == 'completed':
            print(f"  ZIP path: {project.zip_file_path}")
            print(f"  Repo dir: {project.repo_directory}")
            
            # Check action logs
            all_logs = PipelineActionLog.objects.filter(project=project)
            print(f"\n  Total action logs: {all_logs.count()}")
            stages = set()
            for log in all_logs:
                stages.add(log.stage)
                rag_used = log.details.get('rag_used', None)
                rag_info = f" [RAG: {'YES' if rag_used else 'NO'}]" if rag_used is not None else ""
                print(f"    [{log.stage}] {log.agent}: {log.action}{rag_info}")
            
            print(f"\n  Stages covered: {sorted(stages)}")
            
            # Check generated files
            from pathlib import Path
            if project.repo_directory and Path(project.repo_directory).exists():
                repo = Path(project.repo_directory)
                files = list(repo.rglob('*'))
                file_list = [str(f.relative_to(repo)) for f in files if f.is_file()]
                print(f"\n  Generated files: {len(file_list)}")
                for f in sorted(file_list)[:20]:
                    print(f"    {f}")
                if len(file_list) > 20:
                    print(f"    ... and {len(file_list) - 20} more")
                
                # Check requirements.txt for version
                req_path = repo / 'requirements.txt'
                if req_path.exists():
                    print(f"\n  requirements.txt:")
                    print(f"    {req_path.read_text(encoding='utf-8')[:300]}")
                
                # Check package.json for version
                pkg_path = repo / 'package.json'
                if pkg_path.exists():
                    print(f"\n  package.json:")
                    print(f"    {pkg_path.read_text(encoding='utf-8')[:300]}")
            
            print("\n=== PIPELINE VERIFICATION: PASSED ===")
        elif project.status == 'failed':
            print(f"  ERROR: {project.error_message}")
            print("\n=== PIPELINE VERIFICATION: FAILED ===")
        else:
            print(f"  Unexpected status: {project.status}")
    
except Exception as e:
    print(f"\nEXCEPTION: {e}")
    traceback.print_exc()
    print("\n=== PIPELINE VERIFICATION: ERROR ===")
