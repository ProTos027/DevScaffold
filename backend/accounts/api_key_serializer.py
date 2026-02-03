from rest_framework import serializers
from .models import APIKey


class APIKeySerializer(serializers.ModelSerializer):
    """Serializer for API Key model."""
    
    api_key = serializers.CharField(write_only=True, required=True)  # Plain text key for input
    
    class Meta:
        model = APIKey
        fields = ('id', 'provider', 'name', 'api_key', 'created_at', 'updated_at')
        read_only_fields = ('id', 'created_at', 'updated_at')
    
    def validate_provider(self, value):
        """Only allow Gemini provider for now. OpenAI and Anthropic support coming later."""
        if value != 'gemini':
            raise serializers.ValidationError("Only Gemini API keys are currently supported. OpenAI and Anthropic support coming soon.")
        return value
    
    def create(self, validated_data):
        """Create API key with encryption."""
        api_key_plain = validated_data.pop('api_key')
        user = self.context['request'].user
        
        # Create instance
        instance = APIKey(
            user=user,
            provider=validated_data['provider'],
            name=validated_data['name']
        )
        
        # Encrypt and set the key
        instance.set_api_key(api_key_plain)
        instance.save()
        
        return instance
