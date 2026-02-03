from django.core.management.base import BaseCommand
from accounts.models import APIKey
from django.contrib.auth import get_user_model

User = get_user_model()

class Command(BaseCommand):
    help = 'Check Gemini API keys for all users'

    def handle(self, *args, **options):
        for user in User.objects.all():
            keys = APIKey.objects.filter(user=user, provider='gemini')
            self.stdout.write(f"\nUser: {user.username} (ID: {user.id})")
            self.stdout.write(f"  Gemini keys: {keys.count()}")
            for key in keys:
                self.stdout.write(f"    - {key.name} (provider: {key.provider})")
