from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password

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


class APIKeySerializer(serializers.Serializer):
    """Serializer for storing API keys."""
    
    openai_api_key = serializers.CharField(required=False, allow_blank=True, write_only=True)
    anthropic_api_key = serializers.CharField(required=False, allow_blank=True, write_only=True)
    
    def update(self, instance, validated_data):
        if 'openai_api_key' in validated_data:
            instance.set_openai_key(validated_data['openai_api_key'])
        if 'anthropic_api_key' in validated_data:
            instance.set_anthropic_key(validated_data['anthropic_api_key'])
        instance.save()
        return instance


class UserProfileSerializer(serializers.ModelSerializer):
    """Serializer for user profile with API key status."""
    
    has_openai_key = serializers.SerializerMethodField()
    has_anthropic_key = serializers.SerializerMethodField()
    has_github_token = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = (
            'id', 'email', 'username', 'first_name', 'last_name', 'github_username',
            'has_openai_key', 'has_anthropic_key', 'has_github_token',
            'date_joined', 'last_login'
        )
        read_only_fields = ('id', 'email', 'username', 'date_joined', 'last_login', 'github_username')
    
    def get_has_openai_key(self, obj):
        return bool(obj.openai_api_key_encrypted)
    
    def get_has_anthropic_key(self, obj):
        return bool(obj.anthropic_api_key_encrypted)
    
    def get_has_github_token(self, obj):
        return bool(obj.github_access_token_encrypted)
