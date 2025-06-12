from django.test import TestCase
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.contrib.auth import get_user_model
from decimal import Decimal
from datetime import datetime, timezone

from .models import (
    Agent, Medium, Channel, ActionType, Action, 
    TouchpointClass, Touchpoint, Interaction
)
from world.models import Country
from entities.models import Person
from products.models import Product

User = get_user_model()


class MediumModelTest(TestCase):
    """Tests para el modelo Medium"""
    
    def setUp(self):
        """Configuración inicial para los tests"""
        self.medium_data = {
            'name': 'Email Marketing',
            'description': 'Email marketing campaigns',
            'is_active': True
        }
    
    def test_medium_creation(self):
        """Test de creación exitosa de Medium"""
        medium = Medium.objects.create(**self.medium_data)
        
        self.assertEqual(medium.name, 'Email Marketing')
        self.assertEqual(medium.description, 'Email marketing campaigns')
        self.assertTrue(medium.is_active)
        self.assertIsNotNone(medium.created_at)
        self.assertIsNotNone(medium.updated_at)
    
    def test_medium_str_representation(self):
        """Test de representación string del Medium"""
        medium = Medium.objects.create(**self.medium_data)
        self.assertEqual(str(medium), 'Email Marketing')
    
    def test_medium_name_required(self):
        """Test que name es requerido"""
        medium_data = self.medium_data.copy()
        del medium_data['name']
        
        with self.assertRaises(ValidationError):
            medium = Medium(**medium_data)
            medium.full_clean()
    
    def test_medium_name_max_length(self):
        """Test de longitud máxima del name"""
        long_name = 'x' * 256  # Más de 255 caracteres
        medium_data = self.medium_data.copy()
        medium_data['name'] = long_name
        
        with self.assertRaises(ValidationError):
            medium = Medium(**medium_data)
            medium.full_clean()
    
    def test_medium_unique_name(self):
        """Test que el name debe ser único"""
        Medium.objects.create(**self.medium_data)
        
        with self.assertRaises(IntegrityError):
            Medium.objects.create(**self.medium_data)
    
    def test_medium_default_values(self):
        """Test de valores por defecto"""
        medium = Medium.objects.create(name='Test Medium')
        
        self.assertTrue(medium.is_active)
        self.assertEqual(medium.description, '')
    
    def test_medium_ordering(self):
        """Test del ordenamiento por defecto"""
        Medium.objects.create(name='Zebra Medium')
        Medium.objects.create(name='Alpha Medium')
        
        mediums = Medium.objects.all()
        self.assertEqual(mediums[0].name, 'Alpha Medium')
        self.assertEqual(mediums[1].name, 'Zebra Medium')


class ChannelModelTest(TestCase):
    """Tests para el modelo Channel"""
    
    def setUp(self):
        """Configuración inicial para los tests"""
        self.medium = Medium.objects.create(
            name='Digital Marketing',
            description='Digital marketing channels'
        )
        
        self.channel_data = {
            'name': 'Facebook Ads',
            'description': 'Facebook advertising campaigns',
            'medium': self.medium,
            'is_active': True
        }
    
    def test_channel_creation(self):
        """Test de creación exitosa de Channel"""
        channel = Channel.objects.create(**self.channel_data)
        
        self.assertEqual(channel.name, 'Facebook Ads')
        self.assertEqual(channel.description, 'Facebook advertising campaigns')
        self.assertEqual(channel.medium, self.medium)
        self.assertTrue(channel.is_active)
        self.assertIsNotNone(channel.created_at)
        self.assertIsNotNone(channel.updated_at)
    
    def test_channel_str_representation(self):
        """Test de representación string del Channel"""
        channel = Channel.objects.create(**self.channel_data)
        self.assertEqual(str(channel), 'Facebook Ads')
    
    def test_channel_name_required(self):
        """Test que name es requerido"""
        channel_data = self.channel_data.copy()
        del channel_data['name']
        
        with self.assertRaises(ValidationError):
            channel = Channel(**channel_data)
            channel.full_clean()
    
    def test_channel_medium_required(self):
        """Test que medium es requerido"""
        channel_data = self.channel_data.copy()
        del channel_data['medium']
        
        with self.assertRaises(ValidationError):
            channel = Channel(**channel_data)
            channel.full_clean()
    
    def test_channel_unique_name_per_medium(self):
        """Test que el name debe ser único por medium"""
        Channel.objects.create(**self.channel_data)
        
        with self.assertRaises(IntegrityError):
            Channel.objects.create(**self.channel_data)
    
    def test_channel_same_name_different_medium(self):
        """Test que se permite el mismo name en diferentes mediums"""
        # Crear primer channel
        Channel.objects.create(**self.channel_data)
        
        # Crear segundo medium
        medium2 = Medium.objects.create(name='Print Marketing')
        
        # Crear channel con mismo nombre pero diferente medium
        channel2_data = self.channel_data.copy()
        channel2_data['medium'] = medium2
        
        channel2 = Channel.objects.create(**channel2_data)
        self.assertEqual(channel2.name, 'Facebook Ads')
        self.assertEqual(channel2.medium, medium2)
    
    def test_channel_cascade_delete_medium(self):
        """Test que al eliminar medium se eliminan sus channels"""
        channel = Channel.objects.create(**self.channel_data)
        channel_id = channel.id
        
        self.medium.delete()
        
        with self.assertRaises(Channel.DoesNotExist):
            Channel.objects.get(id=channel_id)
    
    def test_channel_default_values(self):
        """Test de valores por defecto"""
        channel = Channel.objects.create(
            name='Test Channel',
            medium=self.medium
        )
        
        self.assertTrue(channel.is_active)
        self.assertEqual(channel.description, '')


class ActionTypeModelTest(TestCase):
    """Tests para el modelo ActionType"""
    
    def setUp(self):
        """Configuración inicial para los tests"""
        self.action_type_data = {
            'name': 'Purchase',
            'description': 'Customer purchase action',
            'category': 'conversion',
            'value_weight': Decimal('1.0'),
            'is_active': True
        }
    
    def test_action_type_creation(self):
        """Test de creación exitosa de ActionType"""
        action_type = ActionType.objects.create(**self.action_type_data)
        
        self.assertEqual(action_type.name, 'Purchase')
        self.assertEqual(action_type.description, 'Customer purchase action')
        self.assertEqual(action_type.category, 'conversion')
        self.assertEqual(action_type.value_weight, Decimal('1.0'))
        self.assertTrue(action_type.is_active)
        self.assertIsNotNone(action_type.created_at)
        self.assertIsNotNone(action_type.updated_at)
    
    def test_action_type_str_representation(self):
        """Test de representación string del ActionType"""
        action_type = ActionType.objects.create(**self.action_type_data)
        self.assertEqual(str(action_type), 'Purchase')
    
    def test_action_type_name_required(self):
        """Test que name es requerido"""
        action_type_data = self.action_type_data.copy()
        del action_type_data['name']
        
        with self.assertRaises(ValidationError):
            action_type = ActionType(**action_type_data)
            action_type.full_clean()
    
    def test_action_type_category_choices(self):
        """Test de validación de choices en category"""
        valid_categories = ['awareness', 'consideration', 'conversion', 'retention', 'advocacy']
        
        for category in valid_categories:
            action_type_data = self.action_type_data.copy()
            action_type_data['category'] = category
            action_type_data['name'] = f'Test {category}'
            
            action_type = ActionType.objects.create(**action_type_data)
            self.assertEqual(action_type.category, category)
    
    def test_action_type_invalid_category(self):
        """Test de category inválida"""
        action_type_data = self.action_type_data.copy()
        action_type_data['category'] = 'invalid_category'
        
        with self.assertRaises(ValidationError):
            action_type = ActionType(**action_type_data)
            action_type.full_clean()
    
    def test_action_type_value_weight_validation(self):
        """Test de validación de value_weight"""
        # Test valor negativo
        action_type_data = self.action_type_data.copy()
        action_type_data['value_weight'] = Decimal('-1.0')
        action_type_data['name'] = 'Negative Weight Test'
        
        with self.assertRaises(ValidationError):
            action_type = ActionType(**action_type_data)
            action_type.full_clean()
        
        # Test valor muy grande
        action_type_data['value_weight'] = Decimal('100.0')
        action_type_data['name'] = 'Large Weight Test'
        
        with self.assertRaises(ValidationError):
            action_type = ActionType(**action_type_data)
            action_type.full_clean()
    
    def test_action_type_unique_name(self):
        """Test que el name debe ser único"""
        ActionType.objects.create(**self.action_type_data)
        
        with self.assertRaises(IntegrityError):
            ActionType.objects.create(**self.action_type_data)
    
    def test_action_type_default_values(self):
        """Test de valores por defecto"""
        action_type = ActionType.objects.create(name='Test Action')
        
        self.assertTrue(action_type.is_active)
        self.assertEqual(action_type.description, '')
        self.assertEqual(action_type.category, 'awareness')
        self.assertEqual(action_type.value_weight, Decimal('0.0'))


class ActionModelTest(TestCase):
    """Tests para el modelo Action"""
    
    def setUp(self):
        """Configuración inicial para los tests"""
        self.action_type = ActionType.objects.create(
            name='Click',
            category='consideration',
            value_weight=Decimal('0.5')
        )
        
        self.country = Country.objects.create(
            name='Test Country',
            code='TC'
        )
        
        self.person = Person.objects.create(
            first_name='Test',
            fathers_name='Person',
            country_of_nationality=self.country
        )
        
        self.product = Product.objects.create(
            name='Test Product',
            description='Test product description'
        )
        
        self.action_data = {
            'action_type': self.action_type,
            'entity': self.person,
            'product': self.product,
            'value': Decimal('10.50'),
            'metadata': {'campaign': 'summer2024', 'source': 'google'},
            'timestamp': datetime.now(timezone.utc)
        }
    
    def test_action_creation(self):
        """Test de creación exitosa de Action"""
        action = Action.objects.create(**self.action_data)
        
        self.assertEqual(action.action_type, self.action_type)
        self.assertEqual(action.entity, self.entity)
        self.assertEqual(action.product, self.product)
        self.assertEqual(action.value, Decimal('10.50'))
        self.assertEqual(action.metadata['campaign'], 'summer2024')
        self.assertIsNotNone(action.timestamp)
        self.assertIsNotNone(action.created_at)
    
    def test_action_str_representation(self):
        """Test de representación string del Action"""
        action = Action.objects.create(**self.action_data)
        expected_str = f"Click by {self.entity.name} on {self.product.name}"
        self.assertEqual(str(action), expected_str)
    
    def test_action_required_fields(self):
        """Test de campos requeridos"""
        # Test sin action_type
        action_data = self.action_data.copy()
        del action_data['action_type']
        
        with self.assertRaises(ValidationError):
            action = Action(**action_data)
            action.full_clean()
        
        # Test sin entity
        action_data = self.action_data.copy()
        del action_data['entity']
        
        with self.assertRaises(ValidationError):
            action = Action(**action_data)
            action.full_clean()
    
    def test_action_optional_product(self):
        """Test que product es opcional"""
        action_data = self.action_data.copy()
        del action_data['product']
        
        action = Action.objects.create(**action_data)
        self.assertIsNone(action.product)
    
    def test_action_value_validation(self):
        """Test de validación de value"""
        # Test valor negativo
        action_data = self.action_data.copy()
        action_data['value'] = Decimal('-10.0')
        
        with self.assertRaises(ValidationError):
            action = Action(**action_data)
            action.full_clean()
    
    def test_action_calculated_weighted_value(self):
        """Test del cálculo de weighted_value"""
        action = Action.objects.create(**self.action_data)
        expected_weighted_value = Decimal('10.50') * Decimal('0.5')
        self.assertEqual(action.weighted_value, expected_weighted_value)
    
    def test_action_calculated_weighted_value_no_value(self):
        """Test del weighted_value cuando no hay value"""
        action_data = self.action_data.copy()
        del action_data['value']
        
        action = Action.objects.create(**action_data)
        self.assertEqual(action.weighted_value, Decimal('0'))
    
    def test_action_cascade_deletes(self):
        """Test de eliminación en cascada"""
        action = Action.objects.create(**self.action_data)
        action_id = action.id
        
        # Al eliminar action_type, se debe eliminar la acción
        self.action_type.delete()
        
        with self.assertRaises(Action.DoesNotExist):
            Action.objects.get(id=action_id)
    
    def test_action_metadata_default(self):
        """Test de valor por defecto de metadata"""
        action_data = self.action_data.copy()
        del action_data['metadata']
        
        action = Action.objects.create(**action_data)
        self.assertEqual(action.metadata, {})
    
    def test_action_timestamp_default(self):
        """Test de valor por defecto de timestamp"""
        action_data = self.action_data.copy()
        del action_data['timestamp']
        
        action = Action.objects.create(**action_data)
        self.assertIsNotNone(action.timestamp)


class AgentModelTest(TestCase):
    """Tests para el modelo Agent"""
    
    def setUp(self):
        """Configuración inicial para los tests"""
        self.user = User.objects.create_user(
            username='testagent',
            email='agent@test.com',
            password='testpass123'
        )
        
        self.country = Country.objects.create(
            name='Test Country',
            code='TC'
        )
        
        self.person = Person.objects.create(
            first_name='Test',
            fathers_name='Person',
            country_of_nationality=self.country
        )
        
        self.agent_data = {
            'user': self.user,
            'entity': self.person,
            'employee_id': 'EMP001',
            'position': 'Sales Representative',
            'department': 'Sales',
            'is_active': True
        }
    
    def test_agent_creation(self):
        """Test de creación exitosa de Agent"""
        agent = Agent.objects.create(**self.agent_data)
        
        self.assertEqual(agent.user, self.user)
        self.assertEqual(agent.entity, self.entity)
        self.assertEqual(agent.employee_id, 'EMP001')
        self.assertEqual(agent.position, 'Sales Representative')
        self.assertEqual(agent.department, 'Sales')
        self.assertTrue(agent.is_active)
        self.assertIsNotNone(agent.created_at)
        self.assertIsNotNone(agent.updated_at)
    
    def test_agent_str_representation(self):
        """Test de representación string del Agent"""
        agent = Agent.objects.create(**self.agent_data)
        expected_str = f"{self.user.get_full_name() or self.user.username} ({self.entity.name})"
        self.assertEqual(str(agent), expected_str)
    
    def test_agent_required_fields(self):
        """Test de campos requeridos"""
        # Test sin user
        agent_data = self.agent_data.copy()
        del agent_data['user']
        
        with self.assertRaises(ValidationError):
            agent = Agent(**agent_data)
            agent.full_clean()
        
        # Test sin entity
        agent_data = self.agent_data.copy()
        del agent_data['entity']
        
        with self.assertRaises(ValidationError):
            agent = Agent(**agent_data)
            agent.full_clean()
    
    def test_agent_unique_user_entity(self):
        """Test que la combinación user-entity debe ser única"""
        Agent.objects.create(**self.agent_data)
        
        with self.assertRaises(IntegrityError):
            Agent.objects.create(**self.agent_data)
    
    def test_agent_same_user_different_entity(self):
        """Test que el mismo user puede estar en diferentes entities"""
        # Crear primer agent
        Agent.objects.create(**self.agent_data)
        
        # Crear segunda person
        person2 = Person.objects.create(
            first_name='Second',
            fathers_name='Person',
            country_of_nationality=self.country
        )
        
        # Crear agent con mismo user pero diferente entity
        agent2_data = self.agent_data.copy()
        agent2_data['entity'] = person2
        agent2_data['employee_id'] = 'EMP002'
        
        agent2 = Agent.objects.create(**agent2_data)
        self.assertEqual(agent2.user, self.user)
        self.assertEqual(agent2.entity, person2)
    
    def test_agent_cascade_deletes(self):
        """Test de eliminación en cascada"""
        agent = Agent.objects.create(**self.agent_data)
        agent_id = agent.id
        
        # Al eliminar user, se debe eliminar el agent
        self.user.delete()
        
        with self.assertRaises(Agent.DoesNotExist):
            Agent.objects.get(id=agent_id)
    
    def test_agent_default_values(self):
        """Test de valores por defecto"""
        agent = Agent.objects.create(
            user=self.user,
            entity=self.entity
        )
        
        self.assertTrue(agent.is_active)
        self.assertEqual(agent.employee_id, '')
        self.assertEqual(agent.position, '')
        self.assertEqual(agent.department, '')
    
    def test_agent_employee_id_max_length(self):
        """Test de longitud máxima del employee_id"""
        long_id = 'x' * 51  # Más de 50 caracteres
        agent_data = self.agent_data.copy()
        agent_data['employee_id'] = long_id
        
        with self.assertRaises(ValidationError):
            agent = Agent(**agent_data)
            agent.full_clean()
    
    def test_agent_position_max_length(self):
        """Test de longitud máxima del position"""
        long_position = 'x' * 256  # Más de 255 caracteres
        agent_data = self.agent_data.copy()
        agent_data['position'] = long_position
        
        with self.assertRaises(ValidationError):
            agent = Agent(**agent_data)
            agent.full_clean()
    
    def test_agent_department_max_length(self):
        """Test de longitud máxima del department"""
        long_department = 'x' * 256  # Más de 255 caracteres
        agent_data = self.agent_data.copy()
        agent_data['department'] = long_department
        
        with self.assertRaises(ValidationError):
            agent = Agent(**agent_data)
            agent.full_clean()
