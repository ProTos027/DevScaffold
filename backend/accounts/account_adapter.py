"""
Custom account adapter to handle email-only authentication (no username field).
"""
from allauth.account.adapter import DefaultAccountAdapter
from rest_framework_simplejwt.tokens import RefreshToken


class NoUsernameAccountAdapter(DefaultAccountAdapter):
    """
    Adapter for User model without username field.
    """
    
    def populate_username(self, request, user):
        """
        Override to skip username population since our User model doesn't have a username field.
        We use email as the primary identifier instead.
        """
        # Don't set username - our User model doesn't have this field
        pass
    
    def get_login_redirect_url(self, request):
        """
        Override to redirect to frontend with JWT tokens after login (including OAuth).
        """
        if request.user.is_authenticated:
            # Generate JWT tokens
            refresh = RefreshToken.for_user(request.user)
            # Redirect to frontend with tokens
            return f"http://localhost:5173/auth/github/callback?access={refresh.access_token}&refresh={refresh}"
        return super().get_login_redirect_url(request)
