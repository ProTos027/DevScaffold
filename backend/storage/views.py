from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from django.conf import settings
from decouple import config
import logging
from .manager import cleanup_expired_repositories

logger = logging.getLogger(__name__)

class StorageCleanupView(APIView):
    """
    Webhook endpoint to trigger storage cleanup.
    Protected by CRON_SECRET_KEY header to prevent unauthorized access.
    """
    permission_classes = [AllowAny]
    
    def post(self, request, *args, **kwargs):
        # 1. Get the secret from the incoming request header
        auth_header = request.headers.get('X-Cron-Secret', '')
        
        # 2. Get the expected secret from our environment
        expected_secret = config('CRON_SECRET_KEY', default='')
        
        # 3. Security Check
        if not expected_secret or auth_header != expected_secret:
            logger.warning("Storage cleanup attempted with invalid or missing CRON_SECRET_KEY")
            return Response(
                {"detail": "Unauthorized. Invalid cron secret."},
                status=403
            )
            
        # 4. If secure, run the cleanup manager function
        try:
            cleaned_count = cleanup_expired_repositories()
            logger.info(f"Storage cleanup successful. Removed {cleaned_count} expired repositories.")
            return Response({
                "status": "success",
                "message": f"Cleaned up {cleaned_count} repositories.",
                "deleted_count": cleaned_count
            })
        except Exception as e:
            logger.error(f"Storage cleanup failed: {str(e)}")
            return Response(
                {"detail": "Cleanup process failed.", "error": str(e)},
                status=500
            )
