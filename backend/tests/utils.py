"""
Test utilities and helpers for BackboneOS project.

This module provides:
- Custom test cases and mixins
- Assertion helpers
- Performance testing utilities
- Database testing helpers
- API testing utilities
- Mock helpers
"""

import os
import time
import json
import tempfile
from decimal import Decimal
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Union
from unittest.mock import patch, MagicMock

from django.test import TestCase, TransactionTestCase
from django.test.utils import override_settings
from django.db import connection, transaction
from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse
from django.utils import timezone

from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from rest_framework.response import Response

from .factories import UserFactory, AdminUserFactory

User = get_user_model()


# =============================================================================
# CUSTOM TEST CASES
# =============================================================================

class BaseTestCase(TestCase):
    """Base test case with common utilities."""
    
    def setUp(self):
        """Set up test data."""
        super().setUp()
        self.user = UserFactory()
        self.admin_user = AdminUserFactory()
        self.client = APIClient()
    
    def assert_response_status(self, response: Response, expected_status: int):
        """Assert response status code."""
        self.assertEqual(
            response.status_code, 
            expected_status,
            f"Expected status {expected_status}, got {response.status_code}. "
            f"Response: {response.data if hasattr(response, 'data') else response.content}"
        )
    
    def assert_response_data(self, response: Response, expected_data: Dict[str, Any]):
        """Assert response data contains expected fields."""
        self.assert_response_status(response, status.HTTP_200_OK)
        for key, value in expected_data.items():
            self.assertEqual(response.data[key], value)
    
    def assert_pagination(self, response: Response, expected_count: int = None):
        """Assert response has pagination structure."""
        self.assertIn('count', response.data)
        self.assertIn('next', response.data)
        self.assertIn('previous', response.data)
        self.assertIn('results', response.data)
        
        if expected_count is not None:
            self.assertEqual(response.data['count'], expected_count)
    
    def assert_error_response(self, response: Response, expected_errors: List[str] = None):
        """Assert response contains error information."""
        self.assertGreaterEqual(response.status_code, 400)
        if expected_errors:
            for error in expected_errors:
                self.assertIn(error, str(response.data))


class BaseAPITestCase(APITestCase):
    """Base API test case with authentication helpers."""
    
    def setUp(self):
        """Set up test data."""
        super().setUp()
        self.user = UserFactory()
        self.admin_user = AdminUserFactory()
        self.client = APIClient()
    
    def authenticate_user(self, user: User = None):
        """Authenticate a user for API requests."""
        user = user or self.user
        self.client.force_authenticate(user=user)
        return user
    
    def authenticate_admin(self):
        """Authenticate admin user for API requests."""
        return self.authenticate_user(self.admin_user)
    
    def make_request(self, method: str, url: str, data: Dict = None, 
                    user: User = None, **kwargs) -> Response:
        """Make an authenticated API request."""
        if user:
            self.authenticate_user(user)
        
        method = method.upper()
        if method == 'GET':
            return self.client.get(url, data, **kwargs)
        elif method == 'POST':
            return self.client.post(url, data, format='json', **kwargs)
        elif method == 'PUT':
            return self.client.put(url, data, format='json', **kwargs)
        elif method == 'PATCH':
            return self.client.patch(url, data, format='json', **kwargs)
        elif method == 'DELETE':
            return self.client.delete(url, **kwargs)
        else:
            raise ValueError(f"Unsupported HTTP method: {method}")
    
    def assert_api_success(self, response: Response, expected_status: int = status.HTTP_200_OK):
        """Assert API response is successful."""
        self.assertLess(response.status_code, 400, 
                       f"API request failed with status {response.status_code}: {response.data}")
        if expected_status:
            self.assertEqual(response.status_code, expected_status)
    
    def assert_api_error(self, response: Response, expected_status: int = None):
        """Assert API response contains an error."""
        self.assertGreaterEqual(response.status_code, 400)
        if expected_status:
            self.assertEqual(response.status_code, expected_status)


class PerformanceTestCase(TransactionTestCase):
    """Test case for performance testing."""
    
    def setUp(self):
        """Set up performance test data."""
        super().setUp()
        self.start_time = time.time()
        self.query_count = 0
    
    def tearDown(self):
        """Log performance metrics."""
        super().tearDown()
        end_time = time.time()
        execution_time = end_time - self.start_time
        print(f"\nPerformance Test: {self._testMethodName}")
        print(f"Execution time: {execution_time:.2f} seconds")
        print(f"Database queries: {self.query_count}")
    
    def assert_performance(self, max_time: float, func, *args, **kwargs):
        """Assert function execution time is within limits."""
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        execution_time = end_time - start_time
        
        self.assertLessEqual(
            execution_time, max_time,
            f"Function took {execution_time:.2f}s, expected <= {max_time}s"
        )
        return result
    
    def assert_query_count(self, max_queries: int, func, *args, **kwargs):
        """Assert function executes within query limit."""
        initial_queries = len(connection.queries)
        result = func(*args, **kwargs)
        final_queries = len(connection.queries)
        query_count = final_queries - initial_queries
        
        self.assertLessEqual(
            query_count, max_queries,
            f"Function executed {query_count} queries, expected <= {max_queries}"
        )
        self.query_count = query_count
        return result


# =============================================================================
# ASSERTION HELPERS
# =============================================================================

class AssertionHelpers:
    """Collection of assertion helper methods."""
    
    @staticmethod
    def assert_model_fields(model_instance, expected_fields: Dict[str, Any]):
        """Assert model instance has expected field values."""
        for field_name, expected_value in expected_fields.items():
            actual_value = getattr(model_instance, field_name)
            assert actual_value == expected_value, \
                f"Field '{field_name}': expected {expected_value}, got {actual_value}"
    
    @staticmethod
    def assert_serializer_data(serializer_data: Dict, expected_data: Dict):
        """Assert serializer data contains expected values."""
        for key, expected_value in expected_data.items():
            assert key in serializer_data, f"Key '{key}' not found in serializer data"
            assert serializer_data[key] == expected_value, \
                f"Key '{key}': expected {expected_value}, got {serializer_data[key]}"
    
    @staticmethod
    def assert_response_structure(response: Response, expected_structure: Dict):
        """Assert response has expected structure."""
        def check_structure(data, structure, path=""):
            for key, expected_type in structure.items():
                current_path = f"{path}.{key}" if path else key
                assert key in data, f"Key '{current_path}' not found in response"
                
                if isinstance(expected_type, dict):
                    check_structure(data[key], expected_type, current_path)
                elif expected_type == list:
                    assert isinstance(data[key], list), \
                        f"Expected list at '{current_path}', got {type(data[key])}"
                elif expected_type == str:
                    assert isinstance(data[key], str), \
                        f"Expected string at '{current_path}', got {type(data[key])}"
                elif expected_type == int:
                    assert isinstance(data[key], int), \
                        f"Expected int at '{current_path}', got {type(data[key])}"
                elif expected_type == float:
                    assert isinstance(data[key], (int, float)), \
                        f"Expected number at '{current_path}', got {type(data[key])}"
                elif expected_type == bool:
                    assert isinstance(data[key], bool), \
                        f"Expected bool at '{current_path}', got {type(data[key])}"
        
        check_structure(response.data, expected_structure)
    
    @staticmethod
    def assert_pagination_structure(response: Response):
        """Assert response has pagination structure."""
        required_fields = ['count', 'next', 'previous', 'results']
        for field in required_fields:
            assert field in response.data, f"Pagination field '{field}' not found"
        
        assert isinstance(response.data['count'], int), "Count must be integer"
        assert isinstance(response.data['results'], list), "Results must be list"
        assert response.data['next'] is None or isinstance(response.data['next'], str), \
            "Next must be string or None"
        assert response.data['previous'] is None or isinstance(response.data['previous'], str), \
            "Previous must be string or None"


# =============================================================================
# DATABASE TESTING HELPERS
# =============================================================================

class DatabaseHelpers:
    """Database testing utilities."""
    
    @staticmethod
    def get_query_count():
        """Get current database query count."""
        return len(connection.queries)
    
    @staticmethod
    def reset_query_count():
        """Reset database query count."""
        connection.queries.clear()
    
    @staticmethod
    def assert_query_count(expected_count: int, func, *args, **kwargs):
        """Assert function executes expected number of queries."""
        DatabaseHelpers.reset_query_count()
        result = func(*args, **kwargs)
        actual_count = DatabaseHelpers.get_query_count()
        
        assert actual_count == expected_count, \
            f"Expected {expected_count} queries, got {actual_count}"
        return result
    
    @staticmethod
    def assert_max_query_count(max_count: int, func, *args, **kwargs):
        """Assert function executes within query limit."""
        DatabaseHelpers.reset_query_count()
        result = func(*args, **kwargs)
        actual_count = DatabaseHelpers.get_query_count()
        
        assert actual_count <= max_count, \
            f"Expected <= {max_count} queries, got {actual_count}"
        return result
    
    @staticmethod
    def create_test_data(model_class, count: int = 10, **kwargs):
        """Create test data for a model."""
        objects = []
        for i in range(count):
            obj = model_class.objects.create(**kwargs)
            objects.append(obj)
        return objects
    
    @staticmethod
    def bulk_create_test_data(model_class, data_list: List[Dict]):
        """Bulk create test data."""
        objects = []
        for data in data_list:
            obj = model_class(**data)
            objects.append(obj)
        return model_class.objects.bulk_create(objects)


# =============================================================================
# API TESTING UTILITIES
# =============================================================================

class APITestHelpers:
    """API testing utilities."""
    
    @staticmethod
    def create_test_file(content: str = "test content", filename: str = "test.txt"):
        """Create a test file for upload."""
        return SimpleUploadedFile(
            filename,
            content.encode(),
            content_type="text/plain"
        )
    
    @staticmethod
    def create_test_image(filename: str = "test.jpg"):
        """Create a test image file."""
        # Create a minimal valid JPEG
        jpeg_data = b'\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01\x01\x00H\x00H\x00\x00\xff\xdb\x00C\x00\x08\x06\x06\x07\x06\x05\x08\x07\x07\x07\t\t\x08\n\x0c\x14\r\x0c\x0b\x0b\x0c\x19\x12\x13\x0f\x14\x1d\x1a\x1f\x1e\x1d\x1a\x1c\x1c $.\' ",#\x1c\x1c(7),01444\x1f\'9=82<.342\xff\xc0\x00\x11\x08\x00\x01\x00\x01\x01\x01\x11\x00\x02\x11\x01\x03\x11\x01\xff\xc4\x00\x14\x00\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x08\xff\xc4\x00\x14\x10\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xff\xda\x00\x0c\x03\x01\x00\x02\x11\x03\x11\x00\x3f\x00\xaa\xff\xd9'
        return SimpleUploadedFile(
            filename,
            jpeg_data,
            content_type="image/jpeg"
        )
    
    @staticmethod
    def assert_api_endpoint(client: APIClient, method: str, url: str, 
                          expected_status: int = 200, data: Dict = None,
                          user: User = None, **kwargs):
        """Test an API endpoint with assertions."""
        if user:
            client.force_authenticate(user=user)
        
        method = method.upper()
        if method == 'GET':
            response = client.get(url, data, **kwargs)
        elif method == 'POST':
            response = client.post(url, data, format='json', **kwargs)
        elif method == 'PUT':
            response = client.put(url, data, format='json', **kwargs)
        elif method == 'PATCH':
            response = client.patch(url, data, format='json', **kwargs)
        elif method == 'DELETE':
            response = client.delete(url, **kwargs)
        else:
            raise ValueError(f"Unsupported HTTP method: {method}")
        
        assert response.status_code == expected_status, \
            f"Expected status {expected_status}, got {response.status_code}: {response.data}"
        
        return response
    
    @staticmethod
    def test_crud_endpoints(client: APIClient, base_url: str, model_class,
                          create_data: Dict, update_data: Dict, user: User = None):
        """Test CRUD operations for an API endpoint."""
        if user:
            client.force_authenticate(user=user)
        
        # Test CREATE
        response = client.post(base_url, create_data, format='json')
        assert response.status_code == 201, f"Create failed: {response.data}"
        created_id = response.data['id']
        
        # Test READ (list)
        response = client.get(base_url)
        assert response.status_code == 200, f"List failed: {response.data}"
        assert response.data['count'] >= 1
        
        # Test READ (detail)
        detail_url = f"{base_url}{created_id}/"
        response = client.get(detail_url)
        assert response.status_code == 200, f"Detail failed: {response.data}"
        
        # Test UPDATE
        response = client.patch(detail_url, update_data, format='json')
        assert response.status_code == 200, f"Update failed: {response.data}"
        
        # Test DELETE
        response = client.delete(detail_url)
        assert response.status_code == 204, f"Delete failed: {response.data}"
        
        # Verify deletion
        response = client.get(detail_url)
        assert response.status_code == 404, "Object should be deleted"


# =============================================================================
# MOCK HELPERS
# =============================================================================

class MockHelpers:
    """Mock and patching utilities."""
    
    @staticmethod
    def mock_redis():
        """Mock Redis connection."""
        return patch('django_redis.get_redis_connection')
    
    @staticmethod
    def mock_celery():
        """Mock Celery task execution."""
        return patch('celery.current_app.send_task')
    
    @staticmethod
    def mock_sentry():
        """Mock Sentry error reporting."""
        return patch('sentry_sdk.capture_exception')
    
    @staticmethod
    def mock_external_api():
        """Mock external API calls."""
        return patch('requests.get'), patch('requests.post'), patch('requests.put'), patch('requests.delete')
    
    @staticmethod
    def mock_file_upload():
        """Mock file upload functionality."""
        return patch('django.core.files.storage.default_storage.save')
    
    @staticmethod
    def mock_email():
        """Mock email sending."""
        return patch('django.core.mail.send_mail')
    
    @staticmethod
    def mock_datetime(fixed_time: datetime = None):
        """Mock datetime for consistent testing."""
        if fixed_time is None:
            fixed_time = datetime(2024, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
        return patch('django.utils.timezone.now', return_value=fixed_time)


# =============================================================================
# PERFORMANCE TESTING UTILITIES
# =============================================================================

class PerformanceHelpers:
    """Performance testing utilities."""
    
    @staticmethod
    def measure_execution_time(func, *args, **kwargs):
        """Measure function execution time."""
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        execution_time = end_time - start_time
        return result, execution_time
    
    @staticmethod
    def measure_memory_usage(func, *args, **kwargs):
        """Measure function memory usage."""
        import psutil
        import os
        
        process = psutil.Process(os.getpid())
        start_memory = process.memory_info().rss
        
        result = func(*args, **kwargs)
        
        end_memory = process.memory_info().rss
        memory_usage = end_memory - start_memory
        
        return result, memory_usage
    
    @staticmethod
    def benchmark_function(func, iterations: int = 100, *args, **kwargs):
        """Benchmark function performance over multiple iterations."""
        times = []
        for _ in range(iterations):
            _, execution_time = PerformanceHelpers.measure_execution_time(func, *args, **kwargs)
            times.append(execution_time)
        
        return {
            'min': min(times),
            'max': max(times),
            'avg': sum(times) / len(times),
            'median': sorted(times)[len(times) // 2],
            'times': times
        }


# =============================================================================
# TEST DATA GENERATORS
# =============================================================================

class TestDataGenerators:
    """Generate test data for various scenarios."""
    
    @staticmethod
    def generate_user_data(**overrides):
        """Generate user test data."""
        from faker import Faker
        fake = Faker()
        
        data = {
            'username': fake.user_name(),
            'email': fake.email(),
            'first_name': fake.first_name(),
            'last_name': fake.last_name(),
            'password': 'testpass123',
        }
        data.update(overrides)
        return data
    
    @staticmethod
    def generate_product_data(**overrides):
        """Generate product test data."""
        from faker import Faker
        fake = Faker()
        
        data = {
            'name': fake.sentence(nb_words=3),
            'code': fake.bothify(text='PROD####'),
            'description': fake.text(max_nb_chars=200),
            'base_price': Decimal(str(fake.pydecimal(left_digits=4, right_digits=2, positive=True))),
            'currency_code': fake.random_element(elements=('PEN', 'USD', 'EUR')),
        }
        data.update(overrides)
        return data
    
    @staticmethod
    def generate_person_data(**overrides):
        """Generate person test data."""
        from faker import Faker
        fake = Faker()
        
        data = {
            'first_name': fake.first_name(),
            'last_name': fake.last_name(),
            'middle_name': fake.first_name(),
            'second_last_name': fake.last_name(),
            'id_number': fake.numerify(text='########'),
            'birthday': fake.date_of_birth(minimum_age=18, maximum_age=65),
        }
        data.update(overrides)
        return data
    
    @staticmethod
    def generate_organization_data(**overrides):
        """Generate organization test data."""
        from faker import Faker
        fake = Faker()
        
        data = {
            'name': fake.company(),
            'legal_name': fake.company() + ' S.A.C.',
            'id_number': fake.numerify(text='###########'),
            'website': fake.url(),
        }
        data.update(overrides)
        return data


# =============================================================================
# INTEGRATION TEST HELPERS
# =============================================================================

class IntegrationTestHelpers:
    """Helpers for integration testing."""
    
    @staticmethod
    def setup_complete_workflow():
        """Set up a complete workflow for integration testing."""
        from .factories import (
            CountryFactory, IndustryFactory, SkillFactory,
            DivisionFactory, ProductCategoryFactory, ProductFactory,
            PersonFactory, OrganizationFactory, UserFactory
        )
        
        # Create base data
        country = CountryFactory()
        industry = IndustryFactory()
        skill = SkillFactory()
        
        # Create product structure
        division = DivisionFactory()
        category = ProductCategoryFactory(division=division)
        product = ProductFactory(category=category)
        
        # Create entities
        person = PersonFactory(country_of_nationality=country)
        organization = OrganizationFactory(country=country, industry=industry)
        user = UserFactory()
        
        return {
            'country': country,
            'industry': industry,
            'skill': skill,
            'division': division,
            'category': category,
            'product': product,
            'person': person,
            'organization': organization,
            'user': user,
        }
    
    @staticmethod
    def test_complete_user_journey(client: APIClient, user_data: Dict):
        """Test a complete user journey."""
        # Register user
        response = client.post('/api/users/register/', user_data, format='json')
        assert response.status_code == 201
        
        # Login user
        login_data = {
            'username': user_data['username'],
            'password': user_data['password']
        }
        response = client.post('/api/auth/login/', login_data, format='json')
        assert response.status_code == 200
        token = response.data['access']
        
        # Authenticate with token
        client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        
        # Access protected endpoint
        response = client.get('/api/users/me/')
        assert response.status_code == 200
        
        return response.data
