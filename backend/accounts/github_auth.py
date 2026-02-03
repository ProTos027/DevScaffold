"""
GitHub OAuth callback handler for JWT token exchange.
"""
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from allauth.socialaccount.models import SocialAccount
from django.contrib.auth import get_user_model

User = get_user_model()


@api_view(['GET'])
@permission_classes([AllowAny])
def github_callback(request):
    """
    Handle GitHub OAuth callback and return JWT tokens.
    This endpoint is called by the frontend after GitHub redirects back.
    """
    # In production, django-allauth handles this automatically
    # For now, we'll create a simple endpoint that the frontend can call
    # after GitHub authentication is complete
    
    # Get the authenticated user from the session (set by django-allauth)
    if not request.user.is_authenticated:
        return Response(
            {'error': 'GitHub authentication failed'},
            status=status.HTTP_401_UNAUTHORIZED
        )
    
    # Generate JWT tokens for the authenticated user
    refresh = RefreshToken.for_user(request.user)
    
    return Response({
        'access': str(refresh.access_token),
        'refresh': str(refresh),
        'user': {
            'id': request.user.id,
            'email': request.user.email,
            'first_name': request.user.first_name,
            'last_name': request.user.last_name,
        }
    })
