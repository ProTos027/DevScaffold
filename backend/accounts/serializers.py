from .models import APIKey
from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
import logging

logger = logging.getLogger(__name__)

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    """Serializer for User model."""
    
    class Meta:
        model = User
        fields = ('id', 'email', 'username', 'first_name', 'last_name', 'date_joined', 'github_username')
        read_only_fields = ('id', 'date_joined')


class RegisterSerializer(serializers.ModelSerializer):
    """Serializer for user registration."""
    
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True, required=True, label='Confirm Password')
    username = serializers.CharField(required=False, allow_blank=True)  # Auto-generated from email if not provided
    
    class Meta:
        model = User
        fields = ('email', 'username', 'password', 'password2', 'first_name', 'last_name')
    
    def validate_username(self, value):
        if value and User.objects.filter(username=value).exists():
            raise serializers.ValidationError("A user with this username already exists.")
        return value
    
    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password": "Password fields didn't match."})
        return attrs
    
    def create(self, validated_data):
        validated_data.pop('password2')
        username = validated_data.pop('username', None)  # Get username if provided, else None
        user = User.objects.create_user(
            email=validated_data['email'],
            password=validated_data['password'],
            username=username,  # Will auto-generate from email if None
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', '')
        )
        return user


class UserProfileSerializer(serializers.ModelSerializer):
    """Serializer for user profile with API key status."""
    
    has_github_token = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = (
            'id', 'email', 'username', 'first_name', 'last_name', 'github_username',
            'has_github_token',
            'date_joined', 'last_login'
        )
        read_only_fields = ('id', 'email', 'username', 'date_joined', 'last_login', 'github_username')
    
    def get_has_github_token(self, obj):
        return bool(obj.github_access_token_encrypted)


class APIKeySerializer(serializers.ModelSerializer):
    """
    Serializer for the APIKey model.
    Handles encryption/decryption of keys and provides a safe preview.
    """
    api_key = serializers.CharField(write_only=True, required=False)
    key_preview = serializers.SerializerMethodField()

    class Meta:
        model = APIKey
        fields = ['id', 'provider', 'name', 'api_key', 'key_preview', 'created_at', 'updated_at']
        read_only_fields = ['id', 'key_preview', 'created_at', 'updated_at']

    def get_key_preview(self, obj):
        decrypted = obj.get_api_key()
        if decrypted:
            if len(decrypted) > 8:
                return f"{decrypted[:4]}...{decrypted[-4:]}"
            return "****"
        return None

    def create(self, validated_data):
        api_key = validated_data.pop('api_key', None)
        user = self.context['request'].user
        try:
            # Instantiate without saving to DB yet
            instance = APIKey(user=user, **validated_data)
            if api_key:
                instance.set_api_key(api_key) # This performs encryption and sets field
            instance.save() # Atomic save after encryption check
            return instance
        except ValueError as e:
            # Catching the ValueError from set_api_key() or encryption failure
            logger.error(f"Validation Error during key creation: {str(e)}")
            raise serializers.ValidationError({"api_key": str(e)})

    def update(self, instance, validated_data):
        api_key = validated_data.pop('api_key', None)
        try:
            if api_key:
                instance.set_api_key(api_key)
            
            for attr, value in validated_data.items():
                setattr(instance, attr, value)
            
            instance.save()
            return instance
        except ValueError as e:
            logger.error(f"Validation Error during key update: {str(e)}")
            raise serializers.ValidationError({"api_key": str(e)})
