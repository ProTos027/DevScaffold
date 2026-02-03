from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from django.utils import timezone
from cryptography.fernet import Fernet
from django.conf import settings


class UserManager(BaseUserManager):
    """Custom user manager for email-based authentication."""
    
    def create_user(self, email, password=None, username=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        if not username:
            # Auto-generate username from email if not provided
            username = email.split('@')[0]
            # Ensure uniqueness
            base_username = username
            counter = 1
            while self.model.objects.filter(username=username).exists():
                username = f"{base_username}{counter}"
                counter += 1
        email = self.normalize_email(email)
        user = self.model(email=email, username=username, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        
        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')
        
        return self.create_user(email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    """
    Custom User model for DevScaffold.
    Users authenticate with email and can store encrypted API keys for LLM providers.
    """
    
    email = models.EmailField(unique=True, db_index=True)
    username = models.CharField(max_length=150, unique=True, db_index=True)
    first_name = models.CharField(max_length=150, blank=True)
    last_name = models.CharField(max_length=150, blank=True)
    
    # API Keys (encrypted)
    openai_api_key_encrypted = models.TextField(blank=True, null=True)
    anthropic_api_key_encrypted = models.TextField(blank=True, null=True)
    
    # GitHub OAuth
    github_access_token_encrypted = models.TextField(blank=True, null=True)
    github_username = models.CharField(max_length=255, blank=True, null=True)
    
    # User status
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(default=timezone.now)
    last_login = models.DateTimeField(null=True, blank=True)
    
    objects = UserManager()
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []
    
    class Meta:
        verbose_name = 'user'
        verbose_name_plural = 'users'
        ordering = ['-date_joined']
    
    def __str__(self):
        return self.username or self.email
    
    def get_full_name(self):
        return f"{self.first_name} {self.last_name}".strip() or self.email
    
    def get_short_name(self):
        return self.first_name or self.email
    
    # Encryption helpers
    @staticmethod
    def _get_cipher():
        """Get Fernet cipher using the encryption key from settings."""
        if not settings.ENCRYPTION_KEY:
            raise ValueError("ENCRYPTION_KEY not set in settings")
        return Fernet(settings.ENCRYPTION_KEY)
    
    def set_openai_key(self, api_key: str):
        """Encrypt and store OpenAI API key."""
        if api_key:
            cipher = self._get_cipher()
            self.openai_api_key_encrypted = cipher.encrypt(api_key.encode()).decode()
        else:
            self.openai_api_key_encrypted = None
    
    def get_openai_key(self) -> str | None:
        """Decrypt and return OpenAI API key."""
        if self.openai_api_key_encrypted:
            cipher = self._get_cipher()
            return cipher.decrypt(self.openai_api_key_encrypted.encode()).decode()
        return None
    
    def set_anthropic_key(self, api_key: str):
        """Encrypt and store Anthropic API key."""
        if api_key:
            cipher = self._get_cipher()
            self.anthropic_api_key_encrypted = cipher.encrypt(api_key.encode()).decode()
        else:
            self.anthropic_api_key_encrypted = None
    
    def get_anthropic_key(self) -> str | None:
        """Decrypt and return Anthropic API key."""
        if self.anthropic_api_key_encrypted:
            cipher = self._get_cipher()
            return cipher.decrypt(self.anthropic_api_key_encrypted.encode()).decode()
        return None
    
    def set_github_token(self, token: str):
        """Encrypt and store GitHub access token."""
        if token:
            cipher = self._get_cipher()
            self.github_access_token_encrypted = cipher.encrypt(token.encode()).decode()
        else:
            self.github_access_token_encrypted = None
    
    def get_github_token(self) -> str | None:
        """Decrypt and return GitHub access token."""
        if self.github_access_token_encrypted:
            cipher = self._get_cipher()
            return cipher.decrypt(self.github_access_token_encrypted.encode()).decode()
        return None


class APIKey(models.Model):
    """
    Model for storing multiple API keys per user.
    Each key has a provider type, user-defined name, and encrypted value.
    
    Currently only Gemini is supported. OpenAI and Anthropic are reserved for future use.
    """
    
    PROVIDER_CHOICES = [
        ('gemini', 'Google Gemini'),  # Currently supported
        ('openai', 'OpenAI'),  # Reserved for future
        ('anthropic', 'Anthropic'),  # Reserved for future
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='api_keys')
    provider = models.CharField(max_length=20, choices=PROVIDER_CHOICES)
    name = models.CharField(max_length=100)  # User-defined name for the key
    api_key_encrypted = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        unique_together = [['user', 'provider', 'name']]  # Prevent duplicate names per provider
    
    def __str__(self):
        return f"{self.user.username} - {self.provider} - {self.name}"
    
    def set_api_key(self, api_key):
        """Encrypt and store the API key."""
        if api_key:
            fernet = Fernet(settings.ENCRYPTION_KEY)
            self.api_key_encrypted = fernet.encrypt(api_key.encode()).decode()
    
    def get_api_key(self):
        """Decrypt and return the API key."""
        if self.api_key_encrypted:
            fernet = Fernet(settings.ENCRYPTION_KEY)
            return fernet.decrypt(self.api_key_encrypted.encode()).decode()
        return None
