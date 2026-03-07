"""
URL configuration for devscaffold project.
"""
from django.contrib import admin
from django.urls import path, include
from devscaffold import temp_admin

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # API endpoints
    path('setup-admin/', temp_admin.create_admin_view),
    path('api/auth/', include('accounts.urls')),
    path('api/projects/', include('projects.urls')),
    path('api/storage/', include('storage.urls')),
    
    # Django Allauth (GitHub OAuth)
    path('accounts/', include('allauth.urls')),
]
