from django.urls import path
from .views import StorageCleanupView

urlpatterns = [
    path('cleanup/', StorageCleanupView.as_view(), name='storage-cleanup'),
]
