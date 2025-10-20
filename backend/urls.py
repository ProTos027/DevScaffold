from django.urls import path
from . import views

urlpatterns= [
    path('register/', views.register_user, name= 'register'),
    path('login/', views.login, name= 'login'),
    path('view_config/', views.view_config, name= 'view_config'),
    path('modded_config/', views.modded_config, name= 'modded_config'),
    path('view_dir/', views.view_dir, name= 'view_dir'),
    path('modded_dir/', views.modded_dir, name= 'modded_dir'),
    path('get_project/', views.get_project, name= 'get_project')
]
