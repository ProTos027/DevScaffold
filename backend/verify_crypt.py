
import os
from cryptography.fernet import Fernet
from decouple import config

key = config('ENCRYPTION_KEY', default='')
print(f"Key Found: '{key[:5]}...{key[-5:] if len(key) > 10 else ''}' (Length: {len(key)})")

try:
    if not key:
        print("ERROR: ENCRYPTION_KEY is empty.")
    else:
        # Simulate what settings.py does
        key_bytes = key.encode()
        f = Fernet(key_bytes)
        print("SUCCESS: Key is a valid Fernet key.")
except Exception as e:
    print(f"FAILED: {str(e)}")
