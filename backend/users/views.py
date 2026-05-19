from django.shortcuts import render
from django.http import JsonResponse
from django.contrib.auth.models import User
from django.conf import settings
from rest_framework import viewsets, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.settings import api_settings as jwt_settings
from django.contrib.auth import authenticate
from .serializers import UserSerializer, UserCreateSerializer


def _set_auth_cookies(response, refresh):
    """Attach access and refresh tokens as httpOnly cookies to a response."""
    access_max_age = int(settings.SIMPLE_JWT['ACCESS_TOKEN_LIFETIME'].total_seconds())
    refresh_max_age = int(settings.SIMPLE_JWT['REFRESH_TOKEN_LIFETIME'].total_seconds())
    cookie_kwargs = {
        'httponly': True,
        'samesite': settings.COOKIE_SAMESITE,
        'secure': settings.COOKIE_SECURE,
    }
    response.set_cookie('access_token', str(refresh.access_token),
                        max_age=access_max_age, **cookie_kwargs)
    response.set_cookie('refresh_token', str(refresh),
                        max_age=refresh_max_age, **cookie_kwargs)


def _clear_auth_cookies(response):
    """Remove auth cookies from a response."""
    response.delete_cookie('access_token')
    response.delete_cookie('refresh_token')


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

    if not username or not password:
        return Response(
            {'error': 'Username y password son requeridos'},
            status=status.HTTP_400_BAD_REQUEST
        )

    user = authenticate(username=username, password=password)
    if not user:
        return Response(
            {'error': 'Credenciales inválidas'},
            status=status.HTTP_401_UNAUTHORIZED
        )

    refresh = RefreshToken.for_user(user)
    serializer = UserSerializer(user)
    response = Response({'user': serializer.data})
    _set_auth_cookies(response, refresh)
    return response


@api_view(['POST'])
@permission_classes([AllowAny])
def jwt_cookie_refresh(request):
    """
    Read the refresh_token httpOnly cookie, rotate it, and issue a fresh
    access_token cookie.  Returns 401 if the cookie is missing or invalid.
    """
    raw_refresh = request.COOKIES.get('refresh_token')
    if not raw_refresh:
        return Response(
            {'error': 'No refresh token cookie found'},
            status=status.HTTP_401_UNAUTHORIZED
        )
    try:
        refresh = RefreshToken(raw_refresh)
        # Honour ROTATE_REFRESH_TOKENS / BLACKLIST_AFTER_ROTATION settings.
        if jwt_settings.ROTATE_REFRESH_TOKENS:
            if jwt_settings.BLACKLIST_AFTER_ROTATION:
                try:
                    refresh.blacklist()
                except AttributeError:
                    pass
            refresh.set_jti()
            refresh.set_exp()
            refresh.set_iat()

        response = Response({'message': 'Token refreshed'})
        _set_auth_cookies(response, refresh)
        return response
    except TokenError as e:
        response = Response({'error': str(e)}, status=status.HTTP_401_UNAUTHORIZED)
        _clear_auth_cookies(response)
        return response


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def jwt_logout(request):
    """Blacklist the refresh token cookie and clear auth cookies."""
    raw_refresh = request.COOKIES.get('refresh_token')
    if raw_refresh:
        try:
            RefreshToken(raw_refresh).blacklist()
        except TokenError:
            pass  # Already invalid — still clear cookies

    response = Response({'message': 'Successfully logged out'})
    _clear_auth_cookies(response)
    return response
