from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from . import views
from .github_auth import github_callback

urlpatterns = [
    # JWT Authentication
    path('login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    
    # Registration
    path('register/', views.RegisterView.as_view(), name='register'),
    
    # User Profile
    path('profile/', views.UserProfileView.as_view(), name='user_profile'),
    
    # API Keys (Old - keep for backward compatibility)
    path('api-keys/', views.APIKeyView.as_view(), name='api_keys'),
    path('check-keys/', views.check_api_keys, name='check_keys'),
    
    # API Keys (New - multi-key management)
    path('keys/', views.APIKeyListCreateView.as_view(), name='api_keys_list_create'),
    path('keys/<int:pk>/', views.APIKeyDeleteView.as_view(), name='api_key_delete'),
    
    # GitHub OAuth Callback
    path('github/callback/', github_callback, name='github_callback'),
]
