from django.db import models
from django.utils import timezone
from accounts.models import APIKey
from core.logger import get_logger

logger = get_logger(__name__)

class RotationManager:
    """
    Manages API key selection and rotation for different providers.
    Implements LRU (Least Recently Used) and quota cooldown enforcement.
    """

    @staticmethod
    def get_best_key(user, provider='gemini'):
        """
        Retrieves the best available API key for a user and provider.
        """
        now = timezone.now()
        
        available_keys = APIKey.objects.filter(
            user=user,
            provider=provider,
            is_active=True
        ).filter(
            models.Q(quota_exhausted_until__isnull=True) | 
            models.Q(quota_exhausted_until__lt=now)
        ).order_by('last_used_at')
        
        best_key = available_keys.first()
        
        if best_key:
            # Update last_used_at on selection
            best_key.last_used_at = now
            best_key.save(update_fields=['last_used_at'])
            return best_key
            
        return None

    @staticmethod
    def mark_exhausted(api_key_obj):
        """
        Marks an API key as exhausted for 24 hours.
        """
        if api_key_obj:
            cooldown = timezone.now() + timezone.timedelta(hours=24)
            api_key_obj.quota_exhausted_until = cooldown
            api_key_obj.save(update_fields=['quota_exhausted_until'])
            logger.warning(f"API Key '{api_key_obj.name}' marked as exhausted until {cooldown}")
