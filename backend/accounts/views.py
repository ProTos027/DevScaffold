from rest_framework import generics, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.views import TokenObtainPairView
from django.contrib.auth import get_user_model

from .serializers import (
    RegisterSerializer,
    UserProfileSerializer,
    APIKeySerializer
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


class APIKeyListCreateView(generics.ListCreateAPIView):
    """
    GET /api/auth/keys/ - List all API keys for current user
    POST /api/auth/keys/ - Create a new API key
    """
    permission_classes = (IsAuthenticated,)
    serializer_class = APIKeySerializer
    
    def get_queryset(self):
        return APIKey.objects.filter(user=self.request.user)


class APIKeyDeleteView(generics.DestroyAPIView):
    """
    DELETE /api/auth/keys/<id>/ - Delete an API key
    """
    permission_classes = (IsAuthenticated,)
    serializer_class = APIKeySerializer
    
    def get_queryset(self):
        return APIKey.objects.filter(user=self.request.user)
 
