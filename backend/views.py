from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import User
from .serializers import UserSerializer

@api_view(['POST'])
def register_user(request):
    #abc= request.get('key')
    #return Response({response dict}, status= status.HTTP_123)
    return Response()

@api_view(['POST'])
def login(request):
    return Response()

@api_view(['GET'])
def view_config(request):
    return Response()

@api_view(['POST'])
def modded_config(request):
    return Response()

@api_view(['GET'])
def view_dir(request):
    return Response()

@api_view(['POST'])
def modded_dir(request):
    return Response()

@api_view(['GET'])
def get_project(request):
    # zip
    return Response()