from rest_framework import generics, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.views import TokenObtainPairView
from django.contrib.auth import get_user_model

from .serializers import (
    RegisterSerializer,
    UserSerializer,
    UserProfileSerializer,
    LegacyAPIKeySerializer as APIKeySerializer,
    APIKeySerializer as NewAPIKeySerializer
)
from .models import APIKey


User = get_user_model()


class RegisterView(generics.CreateAPIView):
    """
    POST /api/auth/register/
    Register a new user.
    """
    queryset = User.objects.all()
    permission_classes = (AllowAny,)
    serializer_class = RegisterSerializer


class UserProfileView(generics.RetrieveUpdateAPIView):
    """
    GET/PUT /api/auth/profile/
    Get or update user profile.
    """
    permission_classes = (IsAuthenticated,)
    serializer_class = UserProfileSerializer
    
    def get_object(self):
        return self.request.user


class APIKeyView(generics.UpdateAPIView):
    """
    PUT /api/auth/api-keys/
    Update user's API keys (OpenAI, Anthropic).
    """
    permission_classes = (IsAuthenticated,)
    serializer_class = APIKeySerializer
    
    def get_object(self):
        return self.request.user
    
    def update(self, request, *args, **kwargs):
        serializer = self.get_serializer(self.get_object(), data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({
            "message": "API keys updated successfully",
            "has_openai_key": bool(serializer.instance.openai_api_key_encrypted),
            "has_anthropic_key": bool(serializer.instance.anthropic_api_key_encrypted)
        })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def check_api_keys(request):
    """
    GET /api/auth/check-keys/
    Check which API keys the user has configured.
    """
    user = request.user
    return Response({
        'has_openai_key': bool(user.openai_api_key_encrypted),
        'has_anthropic_key': bool(user.anthropic_api_key_encrypted),
        'has_github_token': bool(user.github_access_token_encrypted),
    })


class APIKeyListCreateView(generics.ListCreateAPIView):
    """
    GET /api/auth/keys/ - List all API keys for current user
    POST /api/auth/keys/ - Create a new API key
    """
    permission_classes = (IsAuthenticated,)
    serializer_class = NewAPIKeySerializer
    
    def get_queryset(self):
        return APIKey.objects.filter(user=self.request.user)


class APIKeyDeleteView(generics.DestroyAPIView):
    """
    DELETE /api/auth/keys/<id>/ - Delete an API key
    """
    permission_classes = (IsAuthenticated,)
    serializer_class = NewAPIKeySerializer
    
    def get_queryset(self):
        return APIKey.objects.filter(user=self.request.user)
 
