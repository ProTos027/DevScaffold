from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta
from django.conf import settings
import json

User = get_user_model()


class Project(models.Model):
    """
    Main project model representing a generated repository.
    Each project belongs to a user and tracks the pipeline state.
    """
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('spec_building', 'Building Intent Spec'),
        ('review_required', 'Review Required'),
        ('validating', 'Validating'),
        ('planning', 'Building Component Plan'),
        ('code_generation', 'Generating Code'),
        ('assembling', 'Assembling Repository'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='projects')
    name = models.CharField(max_length=255, blank=True)
    prompt = models.TextField()
    model_provider = models.CharField(
        max_length=20,
        choices=[('gemini', 'Google Gemini')],
        default='gemini'
    )
    gemini_model = models.CharField(
        max_length=50,
        choices=[
            ('gemini-3-pro-preview', 'Gemini 3 Pro'),
            ('gemini-3-flash-preview', 'Gemini 3 Flash'),
            ('gemini-2.5-pro', 'Gemini 2.5 Pro'),
            ('gemini-2.5-flash', 'Gemini 2.5 Flash'),
            ('gemini-2.5-flash-lite', 'Gemini 2.5 Flash-Lite'),
            ('gemini-1.5-pro', 'Gemini 1.5 Pro'),
            ('gemini-1.5-flash', 'Gemini 1.5 Flash'),
        ],
        default='gemini-2.5-flash'
    )
    
    # Pipeline status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    current_stage = models.CharField(max_length=50, blank=True)
    progress = models.IntegerField(default=0)  # 0-100
    error_message = models.TextField(blank=True, null=True)
    
    # Selected API key tracking
    gemini_api_key = models.ForeignKey(
        'accounts.APIKey',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='projects'
    )
    
    spec_confirmed = models.BooleanField(default=False)
    
    # File storage
    zip_file_path = models.CharField(max_length=500, blank=True, null=True)
    repo_directory = models.CharField(max_length=500, blank=True, null=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    deletion_scheduled_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['status']),
        ]
    
    def __str__(self):
        return f"{self.name or f'Project {self.id}'} - {self.user.email}"
    
    def mark_completed(self):
        """Mark project as completed and schedule deletion."""
        self.status = 'completed'
        self.completed_at = timezone.now()
        self.deletion_scheduled_at = timezone.now() + timedelta(hours=settings.REPO_RETENTION_HOURS)
        self.progress = 100
        self.save()
    
    def mark_failed(self, error_message: str):
        """Mark project as failed with error message."""
        self.status = 'failed'
        self.error_message = error_message
        self.save()


class IntentSpec(models.Model):
    """
    User-editable Intent Specification.
    This is the single source of truth for project generation.
    Aligned with IntentSpecSchema in backend/pipeline/schemas.py.
    """
    
    project = models.OneToOneField(Project, on_delete=models.CASCADE, related_name='intent_spec')
    
    # Schema fields
    project_type = models.CharField(max_length=100)  # e.g., "url_shortener"
    
    # Stack configuration (JSON)
    stack = models.JSONField(default=dict)  # {backend: {framework, version}, frontend: {...}, database: {...}}
    
    api_type = models.CharField(
        max_length=20,
        choices=[('rest', 'REST'), ('graphql', 'GraphQL'), ('none', 'None')],
        default='rest'
    )
    
    features = models.JSONField(default=list)  # ["authentication", "user_profiles", ...]
    
    architecture = models.CharField(
        max_length=20,
        choices=[('monolith', 'Monolith'), ('microservices', 'Microservices')],
        default='microservices'
    )
    
    data_entities = models.JSONField(default=list)  # [{name, fields}, ...]
    
    auth_method = models.CharField(
        max_length=20,
        choices=[('jwt', 'JWT'), ('session', 'Session'), ('none', 'None')],
        default='none'
    )
    
    # Resilience flags
    vague_intent = models.BooleanField(default=False)
    explanation = models.TextField(blank=True, default="")
    creative_vision = models.TextField(blank=True, default="")
    
    # Metadata
    version = models.IntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Intent Specification'
        verbose_name_plural = 'Intent Specifications'
    
    def __str__(self):
        return f"Intent Spec for {self.project}"
    
    def to_dict(self):
        """Convert to dictionary matching the IntentSpecSchema."""
        return {
            'project_type': self.project_type,
            'stack': self.stack,
            'api_type': self.api_type,
            'features': self.features,
            'architecture': self.architecture,
            'data_entities': self.data_entities,
            'auth_method': self.auth_method,
            'vague_intent': self.vague_intent,
            'explanation': self.explanation,
            'creative_vision': self.creative_vision,
        }
    
    @classmethod
    def from_dict(cls, project, data: dict):
        """Create IntentSpec from dictionary matching IntentSpecSchema."""
        return cls.objects.create(
            project=project,
            project_type=data.get('project_type', 'web_app'),
            stack=data.get('stack', {}),
            api_type=data.get('api_type', 'rest'),
            features=data.get('features', []),
            architecture=data.get('architecture', 'microservices'),
            data_entities=data.get('data_entities', []),
            auth_method=data.get('auth_method', 'none'),
            vague_intent=data.get('vague_intent', False),
            explanation=data.get('explanation', ""),
            creative_vision=data.get('creative_vision', ""),
        )


class ComponentPlan(models.Model):
    """
    System-generated Component Plan.
    Derived from IntentSpec, defines components with responsibilities and dependencies.
    """
    
    project = models.OneToOneField(Project, on_delete=models.CASCADE, related_name='component_plan')
    
    # Components list (JSON) - Aligned with Component Pydantic schema
    # [{id, type, folder, files, responsibilities, depends_on, public_interfaces, data_models}, ...]
    components = models.JSONField(default=list)
    
    # Metadata
    generated_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Component Plan'
        verbose_name_plural = 'Component Plans'
    
    def __str__(self):
        return f"Component Plan for {self.project}"
    
    def to_dict(self):
        """Convert to dictionary."""
        return {'components': self.components}




class ValidationError(models.Model):
    """
    Track validation errors for a project.
    """
    
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='validation_errors')
    rule_name = models.CharField(max_length=100)
    error_message = models.TextField()
    severity = models.CharField(
        max_length=20,
        choices=[('error', 'Error'), ('warning', 'Warning')],
        default='error'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.rule_name}: {self.error_message}"


class PipelineActionLog(models.Model):
    """
    Tracks agent actions during pipeline execution.
    Downstream agents read previous logs to maintain pipeline consistency.
    """
    
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='action_logs')
    stage = models.CharField(max_length=50)        # e.g. 'spec_building', 'code_generation'
    agent = models.CharField(max_length=50)         # e.g. 'spec_builder', 'code_generator'
    action = models.CharField(max_length=100)       # e.g. 'generated_model', 'set_stack'
    details = models.JSONField(default=dict)        # Freeform: {"component": "user_model", ...}
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['created_at']
        verbose_name = 'Pipeline Action Log'
        verbose_name_plural = 'Pipeline Action Logs'
    
    def __str__(self):
        return f"[{self.stage}] {self.agent}: {self.action}"
