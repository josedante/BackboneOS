from django.shortcuts import render
from django.http import JsonResponse
from django.contrib.auth.models import User
from rest_framework import viewsets, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError
from django.contrib.auth import authenticate
from .serializers import UserSerializer, UserCreateSerializer

def home(request):
    return JsonResponse({'message': 'Welcome to the Django + Vue.js + PostgreSQL App!'})

def about(request):
    return render(request, 'users/about.html')

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def get_permissions(self):
        if self.action == 'create':
            permission_classes = []
        else:
            permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]

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

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def current_user(request):
    serializer = UserSerializer(request.user)
    return Response(serializer.data)

@api_view(['POST'])
@permission_classes([AllowAny])
def jwt_login(request):
    username = request.data.get('username')
    password = request.data.get('password')

    if username and password:
        user = authenticate(username=username, password=password)
        if user:
            refresh = RefreshToken.for_user(user)
            serializer = UserSerializer(user)
            return Response({
                'access': str(refresh.access_token),
                'refresh': str(refresh),
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

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def jwt_logout(request):
    """Blacklist the refresh token to invalidate the session."""
    refresh_token = request.data.get('refresh')
    if not refresh_token:
        return Response(
            {'error': 'Refresh token is required'},
            status=status.HTTP_400_BAD_REQUEST
        )
    try:
        token = RefreshToken(refresh_token)
        token.blacklist()
        return Response({'message': 'Successfully logged out'})
    except TokenError as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_400_BAD_REQUEST
        )