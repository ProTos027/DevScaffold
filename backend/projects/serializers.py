"""
DRF serializers for projects app.
"""
from rest_framework import serializers
from .models import Project, IntentSpec, ComponentPlan, DependencyGraph, ValidationError


class IntentSpecSerializer(serializers.ModelSerializer):
    """Serializer for Intent Specification."""
    
    class Meta:
        model = IntentSpec
        fields = ('id', 'project_type', 'complexity', 'stack', 'features', 
                 'architecture', 'data_entities', 'constraints', 'version',
                 'created_at', 'updated_at')
        read_only_fields = ('id', 'created_at', 'updated_at', 'version')


class ComponentPlanSerializer(serializers.ModelSerializer):
    """Serializer for Component Plan."""
    
    class Meta:
        model = ComponentPlan
        fields = ('id', 'components', 'generated_at')
        read_only_fields = ('id', 'components', 'generated_at')


class DependencyGraphSerializer(serializers.ModelSerializer):
    """Serializer for Dependency Graph."""
    
    class Meta:
        model = DependencyGraph
        fields = ('id', 'nodes', 'edges', 'build_order', 'generated_at')
        read_only_fields = ('id', 'nodes', 'edges', 'build_order', 'generated_at')


class ValidationErrorSerializer(serializers.ModelSerializer):
    """Serializer for Validation Errors."""
    
    class Meta:
        model = ValidationError
        fields = ('id', 'rule_name', 'error_message', 'severity', 'created_at')


class ProjectListSerializer(serializers.ModelSerializer):
    """Serializer for project list view."""
    
    class Meta:
        model = Project
        fields = ('id', 'name', 'prompt', 'status', 'progress', 'gemini_model', 'created_at', 'completed_at')
        read_only_fields = ('id', 'status', 'progress', 'created_at', 'completed_at')


class ProjectDetailSerializer(serializers.ModelSerializer):
    """Serializer for detailed project view."""
    
    intent_spec = IntentSpecSerializer(read_only=True)
    component_plan = ComponentPlanSerializer(read_only=True)
    dependency_graph = DependencyGraphSerializer(read_only=True)
    validation_errors = ValidationErrorSerializer(many=True, read_only=True)
    
    class Meta:
        model = Project
        fields = ('id', 'name', 'prompt', 'model_provider', 'status', 'current_stage',
                 'progress', 'error_message', 'zip_file_path', 'created_at', 'updated_at',
                 'completed_at', 'deletion_scheduled_at', 'intent_spec', 'component_plan',
                 'dependency_graph', 'validation_errors')
        read_only_fields = ('id', 'status', 'current_stage', 'progress', 'error_message',
                           'zip_file_path', 'created_at', 'updated_at', 'completed_at',
                           'deletion_scheduled_at')


class ProjectCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating a new project."""
    
    gemini_api_key_id = serializers.IntegerField(write_only=True, required=False, allow_null=True)

    class Meta:
        model = Project
        fields = ('id', 'prompt', 'model_provider', 'gemini_model', 'name', 'status', 'progress', 'created_at', 'gemini_api_key_id')
        read_only_fields = ('id', 'model_provider', 'status', 'progress', 'created_at')
    
    def create(self, validated_data):
        # We don't pop 'prompt' anymore so it gets saved to the Project
        api_key = validated_data.pop('_api_key')
        validated_data.pop('gemini_api_key_id', None) # Pop write-only field not on model
        
        # Create project (user comes from validated_data via view's save(user=...))
        project = Project.objects.create(
            **validated_data
        )
        
        # Store the API key in the project temporarily for orchestrator
        # This will be picked up by the orchestrator triggered in views.py
        project._selected_api_key = api_key.get_api_key()
        
        return project
    
    def validate(self, data):
        user = self.context['request'].user
        
        from accounts.models import APIKey
        
        # Check for Gemini API keys
        gemini_api_key_id = data.get('gemini_api_key_id')
        
        if gemini_api_key_id:
            # Use specific key
            try:
                api_key = APIKey.objects.get(id=gemini_api_key_id, user=user, provider='gemini')
                data['_api_key'] = api_key  # Store for use in create()
            except APIKey.DoesNotExist:
                raise serializers.ValidationError({
                    'gemini_api_key_id': 'Selected Gemini API key not found or does not belong to you'
                })
        else:
            # Use any available Gemini key
            gemini_keys = APIKey.objects.filter(user=user, provider='gemini')
            if not gemini_keys.exists():
                raise serializers.ValidationError({
                    'non_field_errors': 'No Gemini API keys found. Please add a Gemini API key first.'
                })
            data['_api_key'] = gemini_keys.first()  # Use first available key
        
        return data
