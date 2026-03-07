from django.http import HttpResponse
from django.contrib.auth import get_user_model
import threading

def create_admin_view(request):
    def _create():
        User = get_user_model()
        if not User.objects.filter(email='renderadmin@example.com').exists():
            admin = User.objects.create_superuser(
                email='renderadmin@example.com',
                password='adminplaceholder123',
                is_staff=True,
                is_superuser=True
            )
            print("Render Admin created successfully!")
    
    # Run in background to avoid blocking the response
    threading.Thread(target=_create).start()
    return HttpResponse("Admin creation triggered on Render database. Check login in 5 seconds with renderadmin@example.com / adminplaceholder123")
