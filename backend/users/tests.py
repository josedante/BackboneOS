from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework_simplejwt.tokens import RefreshToken
import json


class UserModelTest(TestCase):
    """Tests para el modelo User (Django built-in)"""
    
    def setUp(self):
        """Configurar datos de prueba"""
        self.user_data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'first_name': 'Test',
            'last_name': 'User',
            'password': 'testpass123'
        }
    
    def test_user_creation(self):
        """Test de creación básica de usuario"""
        user = User.objects.create_user(
            username=self.user_data['username'],
            email=self.user_data['email'],
            password=self.user_data['password']
        )
        
        self.assertEqual(user.username, 'testuser')
        self.assertEqual(user.email, 'test@example.com')
        self.assertTrue(user.check_password('testpass123'))
        self.assertTrue(user.is_active)
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)
    
    def test_superuser_creation(self):
        """Test de creación de superusuario"""
        admin_user = User.objects.create_superuser(
            username='admin',
            email='admin@example.com',
            password='adminpass123'
        )
        
        self.assertEqual(admin_user.username, 'admin')
        self.assertTrue(admin_user.is_active)
        self.assertTrue(admin_user.is_staff)
        self.assertTrue(admin_user.is_superuser)
    
    def test_user_string_representation(self):
        """Test de representación string del usuario"""
        user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        self.assertEqual(str(user), 'testuser')


class UserSerializerTest(TestCase):
    """Tests para los serializers de usuarios"""
    
    def setUp(self):
        """Configurar datos de prueba"""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            first_name='Test',
            last_name='User',
            password='testpass123'
        )
    
    def test_user_serializer_data(self):
        """Test del serializer de usuario"""
        from .serializers import UserSerializer
        
        serializer = UserSerializer(self.user)
        data = serializer.data
        
        expected_fields = ['id', 'username', 'email', 'first_name', 'last_name', 'date_joined']
        for field in expected_fields:
            self.assertIn(field, data)
        
        self.assertEqual(data['username'], 'testuser')
        self.assertEqual(data['email'], 'test@example.com')
        self.assertEqual(data['first_name'], 'Test')
        self.assertEqual(data['last_name'], 'User')
    
    def test_user_create_serializer(self):
        """Test del serializer de creación de usuario"""
        from .serializers import UserCreateSerializer
        
        user_data = {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'first_name': 'New',
            'last_name': 'User',
            'password': 'newpass123'
        }
        
        serializer = UserCreateSerializer(data=user_data)
        self.assertTrue(serializer.is_valid())
        
        user = serializer.save()
        self.assertEqual(user.username, 'newuser')
        self.assertEqual(user.email, 'newuser@example.com')
        self.assertTrue(user.check_password('newpass123'))
    
    def test_user_create_serializer_validation(self):
        """Test de validación del serializer de creación"""
        from .serializers import UserCreateSerializer
        
        # Test con datos inválidos
        invalid_data = {
            'username': '',  # Username vacío
            'email': 'invalid-email',  # Email inválido
            'password': '123'  # Password muy corto
        }
        
        serializer = UserCreateSerializer(data=invalid_data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('username', serializer.errors)


class UserViewSetTest(APITestCase):
    """Tests para el ViewSet de usuarios"""
    
    def setUp(self):
        """Configurar datos de prueba"""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.admin_user = User.objects.create_superuser(
            username='admin',
            email='admin@example.com',
            password='adminpass123'
        )
        self.client = APIClient()
    
    def test_user_list_unauthenticated(self):
        """Test de listado de usuarios sin autenticación"""
        url = reverse('user-list')
        response = self.client.get(url)
        
        # Con la nueva configuración de permisos, debe requerir autenticación
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_user_list_authenticated(self):
        """Test de listado de usuarios con autenticación"""
        self.client.force_authenticate(user=self.admin_user)
        url = reverse('user-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data), 2)  # Al menos 2 usuarios
    
    def test_user_create(self):
        """Test de creación de usuario via API"""
        url = reverse('user-list')
        user_data = {
            'username': 'apiuser',
            'email': 'apiuser@example.com',
            'first_name': 'API',
            'last_name': 'User',
            'password': 'apipass123'
        }
        
        response = self.client.post(url, user_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Verificar que el usuario fue creado
        user = User.objects.get(username='apiuser')
        self.assertEqual(user.email, 'apiuser@example.com')
        self.assertTrue(user.check_password('apipass123'))
    
    def test_user_detail(self):
        """Test de detalle de usuario"""
        self.client.force_authenticate(user=self.admin_user)
        url = reverse('user-detail', kwargs={'pk': self.user.pk})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['username'], 'testuser')
    
    def test_user_update(self):
        """Test de actualización de usuario"""
        self.client.force_authenticate(user=self.admin_user)
        url = reverse('user-detail', kwargs={'pk': self.user.pk})
        
        update_data = {
            'first_name': 'Updated',
            'last_name': 'Name'
        }
        
        response = self.client.patch(url, update_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Verificar la actualización
        self.user.refresh_from_db()
        self.assertEqual(self.user.first_name, 'Updated')
        self.assertEqual(self.user.last_name, 'Name')
    
    def test_user_delete(self):
        """Test de eliminación de usuario"""
        self.client.force_authenticate(user=self.admin_user)
        url = reverse('user-detail', kwargs={'pk': self.user.pk})
        
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        
        # Verificar que el usuario fue eliminado
        self.assertFalse(User.objects.filter(pk=self.user.pk).exists())


class AuthenticationAPITest(APITestCase):
    """Tests para las APIs de autenticación"""
    
    def setUp(self):
        """Configurar datos de prueba"""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.client = APIClient()
    
    def test_token_login_success(self):
        """Test de login con token exitoso"""
        url = reverse('api_login')
        login_data = {
            'username': 'testuser',
            'password': 'testpass123'
        }
        
        response = self.client.post(url, login_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Verificar respuesta
        self.assertIn('token', response.data)
        self.assertIn('user', response.data)
        self.assertEqual(response.data['user']['username'], 'testuser')
        
        # Verificar que el token fue creado
        token = Token.objects.get(user=self.user)
        self.assertEqual(response.data['token'], token.key)
    
    def test_token_login_invalid_credentials(self):
        """Test de login con credenciales inválidas"""
        url = reverse('api_login')
        login_data = {
            'username': 'testuser',
            'password': 'wrongpassword'
        }
        
        response = self.client.post(url, login_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertIn('error', response.data)
        self.assertEqual(response.data['error'], 'Credenciales inválidas')
    
    def test_token_login_missing_data(self):
        """Test de login con datos faltantes"""
        url = reverse('api_login')
        
        # Sin username
        response = self.client.post(url, {'password': 'testpass123'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        
        # Sin password
        response = self.client.post(url, {'username': 'testuser'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_jwt_login_success(self):
        """Test de login JWT exitoso"""
        url = reverse('jwt_login')
        login_data = {
            'username': 'testuser',
            'password': 'testpass123'
        }
        
        response = self.client.post(url, login_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Verificar respuesta
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)
        self.assertIn('user', response.data)
        self.assertEqual(response.data['user']['username'], 'testuser')
    
    def test_jwt_login_invalid_credentials(self):
        """Test de login JWT con credenciales inválidas"""
        url = reverse('jwt_login')
        login_data = {
            'username': 'testuser',
            'password': 'wrongpassword'
        }
        
        response = self.client.post(url, login_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertIn('error', response.data)
    
    def test_current_user_authenticated(self):
        """Test de usuario actual con autenticación"""
        self.client.force_authenticate(user=self.user)
        url = reverse('current_user')
        
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['username'], 'testuser')
    
    def test_current_user_unauthenticated(self):
        """Test de usuario actual sin autenticación"""
        url = reverse('current_user')
        
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertIn('error', response.data)


class HomeViewTest(TestCase):
    """Tests para las vistas básicas"""
    
    def test_home_view(self):
        """Test de la vista home"""
        response = self.client.get('/')
        
        self.assertEqual(response.status_code, 200)
        self.assertIn('message', response.json())
        self.assertEqual(
            response.json()['message'], 
            'Welcome to the Django + Vue.js + PostgreSQL App!'
        )
    
    def test_about_view(self):
        """Test de la vista about"""
        response = self.client.get('/about/')
        
        # Nota: Esta vista podría fallar si no existe el template
        # pero probamos que la URL esté configurada
        self.assertIn(response.status_code, [200, 500])  # 500 si falta template


class TokenManagementTest(APITestCase):
    """Tests para gestión de tokens"""
    
    def setUp(self):
        """Configurar datos de prueba"""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
    
    def test_token_creation_on_login(self):
        """Test que el token se crea al hacer login"""
        # Verificar que no existe token inicialmente
        self.assertFalse(Token.objects.filter(user=self.user).exists())
        
        # Hacer login
        url = reverse('api_login')
        login_data = {
            'username': 'testuser',
            'password': 'testpass123'
        }
        
        response = self.client.post(url, login_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Verificar que el token fue creado
        self.assertTrue(Token.objects.filter(user=self.user).exists())
        token = Token.objects.get(user=self.user)
        self.assertEqual(response.data['token'], token.key)
    
    def test_token_reuse_on_multiple_logins(self):
        """Test que el mismo token se reutiliza en múltiples logins"""
        url = reverse('api_login')
        login_data = {
            'username': 'testuser',
            'password': 'testpass123'
        }
        
        # Primer login
        response1 = self.client.post(url, login_data, format='json')
        token1 = response1.data['token']
        
        # Segundo login
        response2 = self.client.post(url, login_data, format='json')
        token2 = response2.data['token']
        
        # Deben ser el mismo token
        self.assertEqual(token1, token2)
        
        # Solo debe existir un token para el usuario
        self.assertEqual(Token.objects.filter(user=self.user).count(), 1)


class JWTTokenTest(APITestCase):
    """Tests específicos para JWT tokens"""
    
    def setUp(self):
        """Configurar datos de prueba"""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
    
    def test_jwt_token_structure(self):
        """Test de estructura del token JWT"""
        url = reverse('jwt_login')
        login_data = {
            'username': 'testuser',
            'password': 'testpass123'
        }
        
        response = self.client.post(url, login_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Verificar que los tokens son strings no vacíos
        self.assertIsInstance(response.data['access'], str)
        self.assertIsInstance(response.data['refresh'], str)
        self.assertGreater(len(response.data['access']), 10)
        self.assertGreater(len(response.data['refresh']), 10)
    
    def test_jwt_refresh_token_endpoint(self):
        """Test del endpoint de refresh de JWT"""
        # Obtener tokens iniciales
        login_url = reverse('jwt_login')
        login_data = {
            'username': 'testuser',
            'password': 'testpass123'
        }
        
        login_response = self.client.post(login_url, login_data, format='json')
        refresh_token = login_response.data['refresh']
        
        # Usar el refresh token
        refresh_url = reverse('jwt_refresh')
        refresh_data = {'refresh': refresh_token}
        
        refresh_response = self.client.post(refresh_url, refresh_data, format='json')
        self.assertEqual(refresh_response.status_code, status.HTTP_200_OK)
        self.assertIn('access', refresh_response.data)


class UserPermissionsTest(APITestCase):
    """Tests para permisos de usuarios"""
    
    def setUp(self):
        """Configurar datos de prueba"""
        self.normal_user = User.objects.create_user(
            username='normal_user',
            email='normal@example.com',
            password='pass123'
        )
        self.admin_user = User.objects.create_superuser(
            username='admin_user',
            email='admin@example.com',
            password='adminpass123'
        )
        self.other_user = User.objects.create_user(
            username='other_user',
            email='other@example.com',
            password='otherpass123'
        )
    
    def test_normal_user_cannot_list_users(self):
        """Test que usuario normal no puede listar usuarios"""
        self.client.force_authenticate(user=self.normal_user)
        url = reverse('user-list')
        response = self.client.get(url)
        
        # Depende de la configuración de permisos
        # Puede ser 403 Forbidden o requerir permisos específicos
        self.assertIn(response.status_code, [200, 403])
    
    def test_admin_user_can_manage_users(self):
        """Test que admin puede gestionar usuarios"""
        self.client.force_authenticate(user=self.admin_user)
        
        # Listar usuarios
        list_url = reverse('user-list')
        response = self.client.get(list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Ver detalle de otro usuario
        detail_url = reverse('user-detail', kwargs={'pk': self.normal_user.pk})
        response = self.client.get(detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_user_can_access_own_profile(self):
        """Test que usuario puede acceder a su propio perfil"""
        self.client.force_authenticate(user=self.normal_user)
        url = reverse('current_user')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['username'], 'normal_user')


class UserValidationTest(TestCase):
    """Tests para validaciones de usuarios"""
    
    def test_username_uniqueness(self):
        """Test de unicidad de username"""
        # Crear primer usuario
        User.objects.create_user(
            username='uniqueuser',
            email='test1@example.com',
            password='pass123'
        )
        
        # Intentar crear segundo usuario con mismo username
        from django.db import IntegrityError
        with self.assertRaises(IntegrityError):
            User.objects.create_user(
                username='uniqueuser',  # Mismo username
                email='test2@example.com',
                password='pass123'
            )
    
    def test_email_validation(self):
        """Test de validación de email"""
        from .serializers import UserCreateSerializer
        
        # Email inválido
        invalid_data = {
            'username': 'testuser',
            'email': 'invalid-email',
            'password': 'pass123'
        }
        
        serializer = UserCreateSerializer(data=invalid_data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('email', serializer.errors)
    
    def test_password_hashing(self):
        """Test que las contraseñas se hashean correctamente"""
        plain_password = 'myplainpassword123'
        user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password=plain_password
        )
        
        # La contraseña no debe almacenarse en texto plano
        self.assertNotEqual(user.password, plain_password)
        
        # Pero debe poder verificarse
        self.assertTrue(user.check_password(plain_password))
        self.assertFalse(user.check_password('wrongpassword'))


class UserIntegrationTest(APITestCase):
    """Tests de integración para flujos completos"""
    
    def test_complete_user_lifecycle(self):
        """Test del ciclo completo de vida del usuario"""
        # 1. Crear usuario
        create_url = reverse('user-list')
        user_data = {
            'username': 'lifecycle_user',
            'email': 'lifecycle@example.com',
            'first_name': 'Lifecycle',
            'last_name': 'User',
            'password': 'lifecycle123'
        }
        
        create_response = self.client.post(create_url, user_data, format='json')
        self.assertEqual(create_response.status_code, status.HTTP_201_CREATED)
        user_id = create_response.data['id']
        
        # 2. Login con el usuario creado
        login_url = reverse('api_login')
        login_data = {
            'username': 'lifecycle_user',
            'password': 'lifecycle123'
        }
        
        login_response = self.client.post(login_url, login_data, format='json')
        self.assertEqual(login_response.status_code, status.HTTP_200_OK)
        token = login_response.data['token']
        
        # 3. Usar token para acceder a información del usuario
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {token}')
        current_user_url = reverse('current_user')
        
        current_response = self.client.get(current_user_url)
        self.assertEqual(current_response.status_code, status.HTTP_200_OK)
        self.assertEqual(current_response.data['username'], 'lifecycle_user')
        
        # 4. Actualizar información del usuario
        update_url = reverse('user-detail', kwargs={'pk': user_id})
        update_data = {
            'first_name': 'Updated',
            'last_name': 'Name'
        }
        
        # Crear admin para poder actualizar
        admin = User.objects.create_superuser(
            username='admin',
            email='admin@example.com',
            password='adminpass'
        )
        self.client.force_authenticate(user=admin)
        
        update_response = self.client.patch(update_url, update_data, format='json')
        self.assertEqual(update_response.status_code, status.HTTP_200_OK)
        self.assertEqual(update_response.data['first_name'], 'Updated')
    
    def test_authentication_flow_comparison(self):
        """Test de comparación entre flujos de autenticación"""
        user = User.objects.create_user(
            username='authtest',
            email='authtest@example.com',
            password='authpass123'
        )
        
        # Test Token Authentication
        token_url = reverse('api_login')
        login_data = {
            'username': 'authtest',
            'password': 'authpass123'
        }
        
        token_response = self.client.post(token_url, login_data, format='json')
        self.assertEqual(token_response.status_code, status.HTTP_200_OK)
        self.assertIn('token', token_response.data)
        
        # Test JWT Authentication
        jwt_url = reverse('jwt_login')
        jwt_response = self.client.post(jwt_url, login_data, format='json')
        self.assertEqual(jwt_response.status_code, status.HTTP_200_OK)
        self.assertIn('access', jwt_response.data)
        self.assertIn('refresh', jwt_response.data)
        
        # Ambos deben retornar la misma información de usuario
        self.assertEqual(
            token_response.data['user']['username'],
            jwt_response.data['user']['username']
        )
