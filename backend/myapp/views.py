from django.shortcuts import render
from django.http import JsonResponse
from django.contrib.auth.models import User
from rest_framework import viewsets, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate
from .serializers import UserSerializer, UserCreateSerializer

def home(request):
    return JsonResponse({'message': 'Welcome to the Django + Vue.js + PostgreSQL App!'})

def about(request):
    return render(request, 'myapp/about.html')

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    
    def get_serializer_class(self):
        if self.action == 'create':
            return UserCreateSerializer
        return UserSerializer

@api_view(['POST'])
@permission_classes([AllowAny])
def login(request):
    username = request.data.get('username')
    password = request.data.get('password')
    
    if username and password:
        user = authenticate(username=username, password=password)
        if user:
            token, created = Token.objects.get_or_create(user=user)
            serializer = UserSerializer(user)
            return Response({
                'token': token.key,
                'user': serializer.data
            })
        else:
            return Response(
                {'error': 'Credenciales inválidas'}, 
                status=status.HTTP_401_UNAUTHORIZED
            )
    else:
        return Response(
            {'error': 'Username y password son requeridos'}, 
            status=status.HTTP_400_BAD_REQUEST
        )