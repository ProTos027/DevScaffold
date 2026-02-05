import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'devscaffold.settings')
django.setup()

from projects.models import Project
from accounts.models import APIKey

print("--- PROJECTS ---")
projects = Project.objects.order_by('-id')[:3]
for p in projects:
    print(f"ID: {p.id} | Name: {p.name} | Status: {p.status} | User: {p.user.username}")
    print(f"  FK Key: {p.gemini_api_key} (ID: {p.gemini_api_key.id if p.gemini_api_key else 'NONE'})")
    print(f"  Gemini Model: {p.gemini_model}")
    print(f"  Error: {p.error_message}")
    print("-" * 40)

print("\n--- API KEYS ---")
keys = APIKey.objects.all()
for k in keys:
    print(f"ID: {k.id} | User: {k.user.username} | Provider: {k.provider} | Name: {k.name} | Has Encrypted: {bool(k.api_key_encrypted)}")

print("\n--- FALLBACK TEST ---")
last_p = Project.objects.order_by('-id').first()
if last_p:
    fallback_keys = APIKey.objects.filter(user=last_p.user, provider='gemini')
    print(f"Fallback keys for user {last_p.user.username} (provider='gemini'): {fallback_keys.count()}")
    for k in fallback_keys:
        try:
            val = k.get_api_key()
            print(f"  Key '{k.name}' (ID: {k.id}) -> Decrypted Length: {len(val) if val else 'None/Empty'}")
        except Exception as e:
            print(f"  Key '{k.name}' (ID: {k.id}) -> DECRYPTION FAILED: {e}")
