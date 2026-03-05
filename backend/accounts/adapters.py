"""
Custom adapter for django-allauth to handle GitHub OAuth with JWT tokens.
"""
from allauth.account.adapter import DefaultAccountAdapter
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from allauth.account.utils import user_email, user_field
from allauth.utils import valid_email_or_none
from django.conf import settings
from django.shortcuts import redirect
from rest_framework_simplejwt.tokens import RefreshToken


class AccountAdapter(DefaultAccountAdapter):
    """
    Adapter for standard email authentication.
    """
    def get_login_redirect_url(self, request):
        """
        Redirect to frontend with JWT tokens after login.
        """
        if request.user.is_authenticated:
            refresh = RefreshToken.for_user(request.user)
            return f"{settings.FRONTEND_URL}/auth/callback?access={refresh.access_token}&refresh={refresh}"
        return super().get_login_redirect_url(request)


class CustomSocialAccountAdapter(DefaultSocialAccountAdapter):
    """
    Adapter for Social (GitHub) authentication.
    """
    def populate_user(self, request, sociallogin, data):
        """
        Override to populate user.
        """
        user = sociallogin.user
        
        # Get data from social provider
        email = data.get('email')
        first_name = data.get('first_name')
        last_name = data.get('last_name')
        name = data.get('name')
        github_username = data.get('login')  # GitHub username is in 'login' field
        
        # Set email
        user_email(user, valid_email_or_none(email) or '')
        
        # Set username - prefer GitHub username, fallback to email prefix
        if github_username:
            user.username = github_username
            user.github_username = github_username
        elif email:
            user.username = email.split('@')[0]
        
        # Set name fields
        name_parts = (name or '').partition(' ')
        user_field(user, 'first_name', first_name or name_parts[0])
        user_field(user, 'last_name', last_name or name_parts[2])
        
        return user
    
    def save_user(self, request, sociallogin, form=None):
        """
        Override to save social user.
        """
        user = sociallogin.user
        user.set_unusable_password()
        # Don't call get_account_adapter().save_user() which tries to set username
        # Just save the social login directly
        sociallogin.save(request)
        return user
    
    def get_login_redirect_url(self, request):
        """
        After successful GitHub OAuth, redirect to frontend with JWT tokens.
        """
        # Generate JWT tokens for the authenticated user
        refresh = RefreshToken.for_user(request.user)
        
        # Redirect to frontend
        return f"{settings.FRONTEND_URL}/auth/github/callback?access={refresh.access_token}&refresh={refresh}"
