"""
Pytest configuration and fixtures for BackboneOS project.

This module provides:
- Global pytest configuration
- Shared fixtures for all tests
- Test database setup and teardown
- Mock configurations
- Test data factories
- Authentication helpers
- Performance testing utilities
"""

import os
import sys
import pytest
import django
from django.conf import settings
from django.test.utils import get_runner
from django.core.management import call_command
from django.contrib.auth import get_user_model
from django.db import connection
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken
from unittest.mock import patch, MagicMock
import tempfile
import shutil

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Configure Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.test_settings')
django.setup()

User = get_user_model()


# =============================================================================
# PYTEST CONFIGURATION
# =============================================================================

def pytest_configure(config):
    """Configure pytest with Django settings."""
    from django.conf import settings
    settings.configure(
        **{
            'DATABASES': {
                'default': {
                    'ENGINE': 'django.db.backends.sqlite3',
                    'NAME': ':memory:',
                }
            },
            'INSTALLED_APPS': [
                'django.contrib.auth',
                'django.contrib.contenttypes',
                'django.contrib.sessions',
                'rest_framework',
                'rest_framework_simplejwt',
                'users',
                'world',
                'products',
                'entities',
                'interactions',
                'our_institution',
                'offers',
                'campaigns',
            ],
            'SECRET_KEY': 'test-secret-key',
            'USE_TZ': True,
        }
    )


def pytest_collection_modifyitems(config, items):
    """Modify test collection to add markers and configure test execution."""
    # Add markers based on test file names
    for item in items:
        # Add markers based on test file location
        if 'test_' in item.nodeid:
            if 'api' in item.nodeid.lower():
                item.add_marker(pytest.mark.api)
            if 'model' in item.nodeid.lower():
                item.add_marker(pytest.mark.models)
            if 'serializer' in item.nodeid.lower():
                item.add_marker(pytest.mark.serializers)
            if 'view' in item.nodeid.lower():
                item.add_marker(pytest.mark.views)
            if 'integration' in item.nodeid.lower():
                item.add_marker(pytest.mark.integration)
            if 'performance' in item.nodeid.lower():
                item.add_marker(pytest.mark.performance)
                item.add_marker(pytest.mark.slow)
            if 'auth' in item.nodeid.lower():
                item.add_marker(pytest.mark.auth)
            if 'celery' in item.nodeid.lower():
                item.add_marker(pytest.mark.celery)
            if 'redis' in item.nodeid.lower():
                item.add_marker(pytest.mark.redis)
            if 'database' in item.nodeid.lower():
                item.add_marker(pytest.mark.database)
            if 'external' in item.nodeid.lower():
                item.add_marker(pytest.mark.external)
            if 'smoke' in item.nodeid.lower():
                item.add_marker(pytest.mark.smoke)
        
        # Default to unit test if no specific marker
        if not any(marker.name in ['api', 'models', 'serializers', 'views', 
                                 'integration', 'performance', 'auth', 
                                 'celery', 'redis', 'database', 'external', 'smoke'] 
                  for marker in item.iter_markers()):
            item.add_marker(pytest.mark.unit)


# =============================================================================
# DATABASE FIXTURES
# =============================================================================

@pytest.fixture(scope='session')
def django_db_setup(django_db_setup, django_db_blocker):
    """Set up test database with fixtures."""
    with django_db_blocker.unblock():
        # Load initial data if needed
        try:
            call_command('loaddata', 'initial_data.json', verbosity=0)
        except Exception:
            pass  # Fixture file might not exist


@pytest.fixture(autouse=True)
def enable_db_access_for_all_tests(db):
    """Enable database access for all tests."""
    pass


# =============================================================================
# USER AND AUTHENTICATION FIXTURES
# =============================================================================

@pytest.fixture
def user():
    """Create a regular user for testing."""
    return User.objects.create_user(
        username='testuser',
        email='test@example.com',
        password='testpass123',
        first_name='Test',
        last_name='User'
    )


@pytest.fixture
def admin_user():
    """Create an admin user for testing."""
    return User.objects.create_superuser(
        username='admin',
        email='admin@example.com',
        password='adminpass123',
        first_name='Admin',
        last_name='User'
    )


@pytest.fixture
def api_client():
    """Create an API client for testing."""
    return APIClient()


@pytest.fixture
def authenticated_client(api_client, user):
    """Create an authenticated API client."""
    api_client.force_authenticate(user=user)
    return api_client


@pytest.fixture
def admin_client(api_client, admin_user):
    """Create an authenticated admin API client."""
    api_client.force_authenticate(user=admin_user)
    return api_client


@pytest.fixture
def jwt_token(user):
    """Create a JWT token for a user."""
    refresh = RefreshToken.for_user(user)
    return {
        'access': str(refresh.access_token),
        'refresh': str(refresh),
    }


@pytest.fixture
def jwt_client(api_client, jwt_token):
    """Create an API client with JWT authentication."""
    api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {jwt_token["access"]}')
    return api_client


# =============================================================================
# MODEL FIXTURES
# =============================================================================

@pytest.fixture
def country():
    """Create a test country."""
    from world.models import Country
    return Country.objects.create(
        iso3_code='PER',
        iso2_code='PE',
        name='Perú',
        official_name='República del Perú',
        phone_code='+51',
        currency_code='PEN'
    )


@pytest.fixture
def industry():
    """Create a test industry."""
    from world.models import Industry
    return Industry.objects.create(
        name='Tecnología',
        code='TECH',
        description='Sector tecnológico'
    )


@pytest.fixture
def skill():
    """Create a test skill."""
    from world.models import Skill
    return Skill.objects.create(
        name='Python',
        code='PY',
        skill_type=Skill.TECHNICAL,
        description='Programación en Python'
    )


@pytest.fixture
def division():
    """Create a test division."""
    from products.models import Division
    return Division.objects.create(
        name='Tecnología',
        code='TECH',
        description='División de productos tecnológicos'
    )


@pytest.fixture
def product_category(division):
    """Create a test product category."""
    from products.models import ProductCategory
    return ProductCategory.objects.create(
        name='Software',
        code='SOFT',
        description='Categoría de software',
        division=division
    )


@pytest.fixture
def product(product_category):
    """Create a test product."""
    from products.models import Product
    from decimal import Decimal
    from datetime import timedelta
    
    return Product.objects.create(
        name='Sistema Web',
        code='SYS001',
        description='Sistema web avanzado',
        category=product_category,
        base_price=Decimal('1500.00'),
        currency_code='PEN',
        duration=timedelta(hours=40)
    )


@pytest.fixture
def person(country):
    """Create a test person."""
    from entities.models import Person
    from world.models import PersonalIDType
    
    id_type = PersonalIDType.objects.create(
        name='DNI',
        code='DNI',
        country=country
    )
    
    return Person.objects.create(
        first_name='Juan',
        last_name='Pérez',
        country_of_nationality=country,
        id_type=id_type,
        id_number='12345678'
    )


@pytest.fixture
def organization(country, industry):
    """Create a test organization."""
    from entities.models import Organization
    from world.models import OrganizationType, OrganizationalIDType
    
    org_type = OrganizationType.objects.create(
        name='SAC',
        code='SAC'
    )
    
    org_id_type = OrganizationalIDType.objects.create(
        name='RUC',
        code='RUC',
        country=country
    )
    
    return Organization.objects.create(
        name='Tech Corp',
        legal_name='Tech Corporation S.A.C.',
        org_type=org_type,
        industry=industry,
        country=country,
        id_type=org_id_type,
        id_number='20123456789'
    )


# =============================================================================
# MOCK FIXTURES
# =============================================================================

@pytest.fixture
def mock_redis():
    """Mock Redis for testing."""
    with patch('django_redis.get_redis_connection') as mock:
        mock_redis_instance = MagicMock()
        mock.return_value = mock_redis_instance
        yield mock_redis_instance


@pytest.fixture
def mock_celery():
    """Mock Celery for testing."""
    with patch('celery.current_app.send_task') as mock:
        yield mock


@pytest.fixture
def mock_sentry():
    """Mock Sentry for testing."""
    with patch('sentry_sdk.capture_exception') as mock:
        yield mock


@pytest.fixture
def mock_external_api():
    """Mock external API calls."""
    with patch('requests.get') as mock_get, \
         patch('requests.post') as mock_post, \
         patch('requests.put') as mock_put, \
         patch('requests.delete') as mock_delete:
        
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = {'status': 'success'}
        
        mock_post.return_value.status_code = 201
        mock_post.return_value.json.return_value = {'id': 1, 'status': 'created'}
        
        mock_put.return_value.status_code = 200
        mock_put.return_value.json.return_value = {'status': 'updated'}
        
        mock_delete.return_value.status_code = 204
        
        yield {
            'get': mock_get,
            'post': mock_post,
            'put': mock_put,
            'delete': mock_delete
        }


# =============================================================================
# TEMPORARY FILES FIXTURES
# =============================================================================

@pytest.fixture
def temp_media_dir():
    """Create a temporary media directory for testing."""
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    shutil.rmtree(temp_dir)


@pytest.fixture
def temp_file():
    """Create a temporary file for testing."""
    with tempfile.NamedTemporaryFile(delete=False) as f:
        f.write(b'test content')
        temp_file_path = f.name
    
    yield temp_file_path
    
    # Clean up
    if os.path.exists(temp_file_path):
        os.unlink(temp_file_path)


# =============================================================================
# PERFORMANCE TESTING FIXTURES
# =============================================================================

@pytest.fixture
def performance_monitor():
    """Monitor performance metrics during tests."""
    import time
    import psutil
    import os
    
    process = psutil.Process(os.getpid())
    
    start_time = time.time()
    start_memory = process.memory_info().rss
    
    yield {
        'start_time': start_time,
        'start_memory': start_memory,
        'process': process
    }
    
    end_time = time.time()
    end_memory = process.memory_info().rss
    
    print(f"\nPerformance Metrics:")
    print(f"Execution time: {end_time - start_time:.2f} seconds")
    print(f"Memory usage: {(end_memory - start_memory) / 1024 / 1024:.2f} MB")


@pytest.fixture
def query_counter():
    """Count database queries during tests."""
    from django.db import connection
    from django.test.utils import override_settings
    
    with override_settings(DEBUG=True):
        initial_queries = len(connection.queries)
        yield connection.queries
        final_queries = len(connection.queries)
        query_count = final_queries - initial_queries
        print(f"\nDatabase queries executed: {query_count}")


# =============================================================================
# TEST DATA FIXTURES
# =============================================================================

@pytest.fixture
def sample_data():
    """Create sample data for testing."""
    from world.models import Country, Industry, Skill
    from products.models import Division, ProductCategory, Product
    from entities.models import Person, Organization
    from decimal import Decimal
    from datetime import timedelta
    
    # Create countries
    peru = Country.objects.create(
        iso3_code='PER',
        iso2_code='PE',
        name='Perú',
        official_name='República del Perú'
    )
    
    colombia = Country.objects.create(
        iso3_code='COL',
        iso2_code='CO',
        name='Colombia',
        official_name='República de Colombia'
    )
    
    # Create industries
    tech_industry = Industry.objects.create(
        name='Tecnología',
        code='TECH'
    )
    
    # Create skills
    python_skill = Skill.objects.create(
        name='Python',
        code='PY',
        skill_type=Skill.TECHNICAL
    )
    
    # Create divisions and categories
    tech_division = Division.objects.create(
        name='Tecnología',
        code='TECH'
    )
    
    software_category = ProductCategory.objects.create(
        name='Software',
        code='SOFT',
        division=tech_division
    )
    
    # Create products
    product1 = Product.objects.create(
        name='Sistema Web',
        code='SYS001',
        category=software_category,
        base_price=Decimal('1500.00')
    )
    
    product2 = Product.objects.create(
        name='Aplicación Móvil',
        code='APP001',
        category=software_category,
        base_price=Decimal('2000.00')
    )
    
    return {
        'countries': [peru, colombia],
        'industries': [tech_industry],
        'skills': [python_skill],
        'divisions': [tech_division],
        'categories': [software_category],
        'products': [product1, product2]
    }


# =============================================================================
# UTILITY FIXTURES
# =============================================================================

@pytest.fixture
def freeze_time():
    """Freeze time for testing."""
    from freezegun import freeze_time
    with freeze_time('2024-01-01 12:00:00') as frozen_time:
        yield frozen_time


@pytest.fixture
def mock_datetime():
    """Mock datetime for testing."""
    from unittest.mock import patch
    import datetime
    
    with patch('datetime.datetime') as mock_dt:
        mock_dt.now.return_value = datetime.datetime(2024, 1, 1, 12, 0, 0)
        mock_dt.utcnow.return_value = datetime.datetime(2024, 1, 1, 12, 0, 0)
        yield mock_dt


# =============================================================================
# TEST HELPERS
# =============================================================================

@pytest.fixture
def assert_queries():
    """Helper to assert database query count."""
    from django.test.utils import override_settings
    from django.db import connection
    
    def _assert_queries(expected_count, func, *args, **kwargs):
        with override_settings(DEBUG=True):
            initial_queries = len(connection.queries)
            result = func(*args, **kwargs)
            final_queries = len(connection.queries)
            actual_count = final_queries - initial_queries
            
            assert actual_count == expected_count, \
                f"Expected {expected_count} queries, got {actual_count}"
            
            return result
    
    return _assert_queries


@pytest.fixture
def assert_performance():
    """Helper to assert performance metrics."""
    import time
    
    def _assert_performance(max_time, func, *args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        execution_time = end_time - start_time
        
        assert execution_time <= max_time, \
            f"Function took {execution_time:.2f}s, expected <= {max_time}s"
        
        return result
    
    return _assert_performance


# =============================================================================
# CLEANUP FIXTURES
# =============================================================================

@pytest.fixture(autouse=True)
def cleanup_test_data():
    """Clean up test data after each test."""
    yield
    
    # Clean up any test-specific data
    from django.core.cache import cache
    cache.clear()


# =============================================================================
# CUSTOM ASSERTIONS
# =============================================================================

def pytest_assertrepr_compare(op, left, right):
    """Custom assertion representations for better error messages."""
    if op == "==" and isinstance(left, dict) and isinstance(right, dict):
        return [
            "Dictionary comparison failed:",
            f"Left:  {left}",
            f"Right: {right}",
        ]
    elif op == "==" and isinstance(left, list) and isinstance(right, list):
        return [
            "List comparison failed:",
            f"Left:  {left}",
            f"Right: {right}",
        ]


# =============================================================================
# TEST MARKERS
# =============================================================================

def pytest_configure(config):
    """Configure custom test markers."""
    config.addinivalue_line(
        "markers", "unit: mark test as a unit test"
    )
    config.addinivalue_line(
        "markers", "integration: mark test as an integration test"
    )
    config.addinivalue_line(
        "markers", "api: mark test as an API test"
    )
    config.addinivalue_line(
        "markers", "slow: mark test as slow running"
    )
    config.addinivalue_line(
        "markers", "performance: mark test as a performance test"
    )
    config.addinivalue_line(
        "markers", "auth: mark test as an authentication test"
    )
    config.addinivalue_line(
        "markers", "models: mark test as a model test"
    )
    config.addinivalue_line(
        "markers", "serializers: mark test as a serializer test"
    )
    config.addinivalue_line(
        "markers", "views: mark test as a view test"
    )
    config.addinivalue_line(
        "markers", "celery: mark test as a Celery task test"
    )
    config.addinivalue_line(
        "markers", "redis: mark test as a Redis related test"
    )
    config.addinivalue_line(
        "markers", "database: mark test as a database related test"
    )
    config.addinivalue_line(
        "markers", "external: mark test as requiring external services"
    )
    config.addinivalue_line(
        "markers", "smoke: mark test as a smoke test"
    )
