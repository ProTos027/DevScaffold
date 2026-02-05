import os
import django
from rest_framework.test import APIRequestFactory

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'devscaffold.settings')
django.setup()

from projects.serializers import ProjectCreateSerializer
from projects.models import Project
from accounts.models import APIKey
from django.contrib.auth import get_user_model

User = get_user_model()
user = User.objects.filter(username='adisriva').first()
if not user:
    print("User 'adisriva' not found")
    exit(1)

factory = APIRequestFactory()
request = factory.post('/api/projects/')
request.user = user

# Get a valid Gemini key
gemini_key = APIKey.objects.filter(user=user, provider='gemini').exclude(api_key_encrypted='').first()
if not gemini_key:
    print("No valid Gemini key found for user")
    exit(1)

print(f"Using key: {gemini_key.name} (ID: {gemini_key.id})")

data = {
    'prompt': 'Testing persistence',
    'gemini_model': 'gemini-2.5-flash',
    'name': 'Test Project',
    'gemini_api_key_id': gemini_key.id
}

serializer = ProjectCreateSerializer(data=data, context={'request': request})
if serializer.is_valid():
    project = serializer.save()
    print(f"Project Created! ID: {project.id}")
    print(f"Project gemini_api_key FK: {project.gemini_api_key} (ID: {project.gemini_api_key.id if project.gemini_api_key else 'NONE'})")
    
    # Reload from DB
    p_reload = Project.objects.get(id=project.id)
    print(f"Reloaded gemini_api_key FK: {p_reload.gemini_api_key} (ID: {p_reload.gemini_api_key.id if p_reload.gemini_api_key else 'NONE'})")
else:
    print(f"Serializer Invalid: {serializer.errors}")
