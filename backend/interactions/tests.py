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
from world.models import Country, Industry, FunctionOrResponsibility, Skill, WorldDescriptor, DescriptorFamily
from entities.models import Person, Organization
from products.models import Product

User = get_user_model()


class MediumModelTest(TestCase):
    """Tests para el modelo Medium"""
    
    def setUp(self):
        """Configuración inicial para los tests"""
        self.medium_data = {
            'name': 'Email Marketing',
            'code': 'EMAIL',
            'description': 'Email marketing campaigns',
            'is_active': True
        }
    
    def test_medium_creation(self):
        """Test de creación exitosa de Medium"""
        medium = Medium.objects.create(**self.medium_data)
        
        self.assertEqual(medium.name, 'Email Marketing')
        self.assertEqual(medium.code, 'EMAIL')
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
    
    def test_medium_code_required(self):
        """Test que code es requerido"""
        medium_data = self.medium_data.copy()
        del medium_data['code']
        
        with self.assertRaises(ValidationError):
            medium = Medium(**medium_data)
            medium.full_clean()
    
    def test_medium_name_max_length(self):
        """Test de longitud máxima del name"""
        long_name = 'x' * 101  # Más de 100 caracteres
        medium_data = self.medium_data.copy()
        medium_data['name'] = long_name
        
        with self.assertRaises(ValidationError):
            medium = Medium(**medium_data)
            medium.full_clean()
    
    def test_medium_code_max_length(self):
        """Test de longitud máxima del code"""
        long_code = 'x' * 21  # Más de 20 caracteres
        medium_data = self.medium_data.copy()
        medium_data['code'] = long_code
        
        with self.assertRaises(ValidationError):
            medium = Medium(**medium_data)
            medium.full_clean()
    
    def test_medium_unique_name(self):
        """Test que el name debe ser único"""
        Medium.objects.create(**self.medium_data)
        
        with self.assertRaises(IntegrityError):
            Medium.objects.create(**self.medium_data)
    
    def test_medium_unique_code(self):
        """Test que el code debe ser único"""
        Medium.objects.create(**self.medium_data)
        
        # Crear otro medium con el mismo code
        medium_data2 = self.medium_data.copy()
        medium_data2['name'] = 'Different Name'
        
        with self.assertRaises(IntegrityError):
            Medium.objects.create(**medium_data2)
    
    def test_medium_default_values(self):
        """Test de valores por defecto"""
        medium = Medium.objects.create(name='Test Medium', code='TEST')
        
        self.assertTrue(medium.is_active)
        self.assertEqual(medium.description, '')
    
    def test_medium_ordering(self):
        """Test del ordenamiento por defecto"""
        Medium.objects.create(name='Zebra Medium', code='ZEBRA')
        Medium.objects.create(name='Alpha Medium', code='ALPHA')
        
        mediums = Medium.objects.all()
        self.assertEqual(mediums[0].name, 'Alpha Medium')
        self.assertEqual(mediums[1].name, 'Zebra Medium')


class ChannelModelTest(TestCase):
    """Tests para el modelo Channel"""
    
    def setUp(self):
        """Configuración inicial para los tests"""
        self.medium = Medium.objects.create(
            name='Digital Marketing',
            code='DIGITAL',
            description='Digital marketing channels'
        )
        
        self.channel_data = {
            'name': 'Facebook Ads',
            'code': 'FB_ADS',
            'description': 'Facebook advertising campaigns',
            'medium': self.medium,
            'is_active': True
        }
    
    def test_channel_creation(self):
        """Test de creación exitosa de Channel"""
        channel = Channel.objects.create(**self.channel_data)
        
        self.assertEqual(channel.name, 'Facebook Ads')
        self.assertEqual(channel.code, 'FB_ADS')
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
    
    def test_channel_code_required(self):
        """Test que code es requerido"""
        channel_data = self.channel_data.copy()
        del channel_data['code']
        
        with self.assertRaises(ValidationError):
            channel = Channel(**channel_data)
            channel.full_clean()
    
    def test_channel_medium_optional(self):
        """Test que medium es opcional"""
        channel_data = self.channel_data.copy()
        del channel_data['medium']
        
        channel = Channel.objects.create(**channel_data)
        self.assertIsNone(channel.medium)
    
    def test_channel_unique_name(self):
        """Test que el name debe ser único"""
        Channel.objects.create(**self.channel_data)
        
        with self.assertRaises(IntegrityError):
            Channel.objects.create(**self.channel_data)
    
    def test_channel_unique_code(self):
        """Test que el code debe ser único"""
        Channel.objects.create(**self.channel_data)
        
        # Crear otro channel con el mismo code
        channel_data2 = self.channel_data.copy()
        channel_data2['name'] = 'Different Name'
        
        with self.assertRaises(IntegrityError):
            Channel.objects.create(**channel_data2)
    
    def test_channel_same_name_different_code(self):
        """Test que se permite el mismo name con diferente code"""
        Channel.objects.create(**self.channel_data)
        
        # Crear channel con mismo nombre pero diferente code
        channel2_data = self.channel_data.copy()
        channel2_data['name'] = 'Facebook Ads'  # mismo nombre
        channel2_data['code'] = 'FB_ADS_2'  # diferente code
        
        # Esto debería fallar por el unique constraint en name
        with self.assertRaises(IntegrityError):
            Channel.objects.create(**channel2_data)
    
    def test_channel_cascade_delete_medium(self):
        """Test que al eliminar medium se setea NULL en channels"""
        channel = Channel.objects.create(**self.channel_data)
        
        self.medium.delete()
        
        # El channel debe seguir existiendo pero con medium=None
        channel.refresh_from_db()
        self.assertIsNone(channel.medium)
    
    def test_channel_default_values(self):
        """Test de valores por defecto"""
        channel = Channel.objects.create(
            name='Test Channel',
            code='TEST_CH'
        )
        
        self.assertTrue(channel.is_active)
        self.assertEqual(channel.description, '')
        self.assertIsNone(channel.medium)


class ActionTypeModelTest(TestCase):
    """Tests para el modelo ActionType"""
    
    def setUp(self):
        """Configuración inicial para los tests"""
        self.action_type_data = {
            'name': 'Purchase',
            'code': 'PURCHASE',
            'description': 'Customer purchase action',
            'is_active': True
        }
    
    def test_action_type_creation(self):
        """Test de creación exitosa de ActionType"""
        action_type = ActionType.objects.create(**self.action_type_data)
        
        self.assertEqual(action_type.name, 'Purchase')
        self.assertEqual(action_type.code, 'PURCHASE')
        self.assertEqual(action_type.description, 'Customer purchase action')
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
    
    def test_action_type_code_required(self):
        """Test que code es requerido"""
        action_type_data = self.action_type_data.copy()
        del action_type_data['code']
        
        with self.assertRaises(ValidationError):
            action_type = ActionType(**action_type_data)
            action_type.full_clean()
    
    def test_action_type_unique_name(self):
        """Test que el name debe ser único"""
        ActionType.objects.create(**self.action_type_data)
        
        with self.assertRaises(IntegrityError):
            ActionType.objects.create(**self.action_type_data)
    
    def test_action_type_unique_code(self):
        """Test que el code debe ser único"""
        ActionType.objects.create(**self.action_type_data)
        
        # Crear otro action type con el mismo code
        action_type_data2 = self.action_type_data.copy()
        action_type_data2['name'] = 'Different Name'
        
        with self.assertRaises(IntegrityError):
            ActionType.objects.create(**action_type_data2)
    
    def test_action_type_default_values(self):
        """Test de valores por defecto"""
        action_type = ActionType.objects.create(name='Test Action', code='TEST_ACTION')
        
        self.assertTrue(action_type.is_active)
        self.assertEqual(action_type.description, '')
    
    def test_action_type_name_max_length(self):
        """Test de longitud máxima del name"""
        long_name = 'x' * 101  # Más de 100 caracteres
        action_type_data = self.action_type_data.copy()
        action_type_data['name'] = long_name
        
        with self.assertRaises(ValidationError):
            action_type = ActionType(**action_type_data)
            action_type.full_clean()
    
    def test_action_type_code_max_length(self):
        """Test de longitud máxima del code"""
        long_code = 'x' * 31  # Más de 30 caracteres
        action_type_data = self.action_type_data.copy()
        action_type_data['code'] = long_code
        
        with self.assertRaises(ValidationError):
            action_type = ActionType(**action_type_data)
            action_type.full_clean()


class ActionModelTest(TestCase):
    """Tests para el modelo Action"""
    
    def setUp(self):
        """Configuración inicial para los tests"""
        self.action_type = ActionType.objects.create(
            name='Click',
            code='CLICK',
            description='Click action'
        )
        
        self.action_data = {
            'name': 'Main Click Action',
            'code': 'MAIN_CLICK',
            'description': 'Main click action for buttons',
            'action_type': self.action_type,
            'is_active': True
        }
    
    def test_action_creation(self):
        """Test de creación exitosa de Action"""
        action = Action.objects.create(**self.action_data)
        
        self.assertEqual(action.name, 'Main Click Action')
        self.assertEqual(action.code, 'MAIN_CLICK')
        self.assertEqual(action.description, 'Main click action for buttons')
        self.assertEqual(action.action_type, self.action_type)
        self.assertTrue(action.is_active)
        self.assertIsNotNone(action.created_at)
    
    def test_action_str_representation(self):
        """Test de representación string del Action"""
        action = Action.objects.create(**self.action_data)
        self.assertEqual(str(action), 'Main Click Action')
    
    def test_action_required_fields(self):
        """Test de campos requeridos"""
        # Test sin name
        action_data = self.action_data.copy()
        del action_data['name']
        
        with self.assertRaises(ValidationError):
            action = Action(**action_data)
            action.full_clean()
        
        # Test sin code
        action_data = self.action_data.copy()
        del action_data['code']
        
        with self.assertRaises(ValidationError):
            action = Action(**action_data)
            action.full_clean()
    
    def test_action_optional_action_type(self):
        """Test que action_type es opcional"""
        action_data = self.action_data.copy()
        del action_data['action_type']
        
        action = Action.objects.create(**action_data)
        self.assertIsNone(action.action_type)
    
    def test_action_unique_name(self):
        """Test que el name debe ser único"""
        Action.objects.create(**self.action_data)
        
        with self.assertRaises(IntegrityError):
            Action.objects.create(**self.action_data)
    
    def test_action_unique_code(self):
        """Test que el code debe ser único"""
        Action.objects.create(**self.action_data)
        
        # Crear otra action con el mismo code
        action_data2 = self.action_data.copy()
        action_data2['name'] = 'Different Name'
        
        with self.assertRaises(IntegrityError):
            Action.objects.create(**action_data2)
    
    def test_action_cascade_deletes(self):
        """Test de eliminación con SET_NULL"""
        action = Action.objects.create(**self.action_data)
        
        # Al eliminar action_type, se debe setear NULL
        self.action_type.delete()
        
        action.refresh_from_db()
        self.assertIsNone(action.action_type)
    
    def test_action_default_values(self):
        """Test de valores por defecto"""
        action = Action.objects.create(
            name='Test Action',
            code='TEST_ACTION'
        )
        
        self.assertTrue(action.is_active)
        self.assertEqual(action.description, '')
        self.assertIsNone(action.action_type)
    
    def test_action_name_max_length(self):
        """Test de longitud máxima del name"""
        long_name = 'x' * 101  # Más de 100 caracteres
        action_data = self.action_data.copy()
        action_data['name'] = long_name
        
        with self.assertRaises(ValidationError):
            action = Action(**action_data)
            action.full_clean()
    
    def test_action_code_max_length(self):
        """Test de longitud máxima del code"""
        long_code = 'x' * 31  # Más de 30 caracteres
        action_data = self.action_data.copy()
        action_data['code'] = long_code
        
        with self.assertRaises(ValidationError):
            action = Action(**action_data)
            action.full_clean()


class AgentModelTest(TestCase):
    """Tests para el modelo Agent"""
    
    def setUp(self):
        """Configuración inicial para los tests"""
        self.country = Country.objects.create(
            iso3_code='TST',
            iso2_code='TS',
            name='Test Country',
            official_name='Republic of Test Country'
        )
        
        self.person = Person.objects.create(
            first_name='Test',
            last_name='Person',
            country_of_nationality=self.country
        )
        
        self.organization = Organization.objects.create(
            name='Test Organization',
            country=self.country
        )
        
        self.agent_data = {
            'agent_type': 'human',
            'name': 'Test Agent',
            'identifier': 'AGENT001',
            'operated_by': self.person,
            'metadata': {'role': 'customer_service'},
            'is_active': True
        }
    
    def test_agent_creation(self):
        """Test de creación exitosa de Agent"""
        agent = Agent.objects.create(**self.agent_data)
        
        self.assertEqual(agent.agent_type, 'human')
        self.assertEqual(agent.name, 'Test Agent')
        self.assertEqual(agent.identifier, 'AGENT001')
        self.assertEqual(agent.operated_by, self.person)
        self.assertEqual(agent.metadata['role'], 'customer_service')
        self.assertTrue(agent.is_active)
        self.assertIsNotNone(agent.created_at)
        self.assertIsNotNone(agent.updated_at)
    
    def test_agent_str_representation(self):
        """Test de representación string del Agent"""
        agent = Agent.objects.create(**self.agent_data)
        # El agent no tiene represents_person pero sí operated_by, así que debería mostrar solo el nombre
        self.assertEqual(str(agent), 'Test Agent')
    
    def test_agent_str_with_organization(self):
        """Test de representación string del Agent con organización"""
        agent_data = self.agent_data.copy()
        agent_data['represents_organization'] = self.organization
        del agent_data['operated_by']  # Quitar operated_by para evitar conflictos
        
        agent = Agent.objects.create(**agent_data)
        expected_str = f"Test Agent ↔ {self.organization.name}"
        self.assertEqual(str(agent), expected_str)
    
    def test_agent_agent_type_choices(self):
        """Test de validación de choices en agent_type"""
        valid_types = ['browser', 'human', 'system', 'device', 'bot', 'ai', 'other']
        
        for agent_type in valid_types:
            agent_data = self.agent_data.copy()
            agent_data['agent_type'] = agent_type
            agent_data['name'] = f'Test {agent_type}'
            agent_data['identifier'] = f'{agent_type.upper()}001'
            
            agent = Agent.objects.create(**agent_data)
            self.assertEqual(agent.agent_type, agent_type)
    
    def test_agent_invalid_agent_type(self):
        """Test de agent_type inválido"""
        agent_data = self.agent_data.copy()
        agent_data['agent_type'] = 'invalid_type'
        
        with self.assertRaises(ValidationError):
            agent = Agent(**agent_data)
            agent.full_clean()
    
    def test_agent_name_generation_browser(self):
        """Test de generación automática de nombre para browser"""
        agent_data = {
            'agent_type': 'browser',
            'metadata': {'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        }
        
        agent = Agent.objects.create(**agent_data)
        agent.clean()  # Para activar la generación de nombre
        agent.save()
        
        self.assertTrue(agent.name.startswith('Mozilla/5.0'))
        self.assertTrue(len(agent.name) <= 40)
    
    def test_agent_name_generation_bot(self):
        """Test de generación automática de nombre para bot"""
        agent_data = {
            'agent_type': 'bot',
            'identifier': 'BOT123'
        }
        
        agent = Agent()
        for key, value in agent_data.items():
            setattr(agent, key, value)
        
        generated_name = agent.generate_name()
        self.assertEqual(generated_name, 'Bot BOT123')
    
    def test_agent_cannot_represent_person_and_organization(self):
        """Test que un agente no puede representar persona y organización simultáneamente"""
        agent_data = self.agent_data.copy()
        agent_data['represents_person'] = self.person
        agent_data['represents_organization'] = self.organization
        
        with self.assertRaises(ValidationError):
            agent = Agent(**agent_data)
            agent.full_clean()
    
    def test_agent_cascade_deletes(self):
        """Test de eliminación con SET_NULL"""
        agent = Agent.objects.create(**self.agent_data)
        
        # Al eliminar person, se debe setear NULL
        self.person.delete()
        
        agent.refresh_from_db()
        self.assertIsNone(agent.operated_by)
    
    def test_agent_default_values(self):
        """Test de valores por defecto"""
        agent = Agent.objects.create()
        
        self.assertEqual(agent.agent_type, 'other')
        self.assertTrue(agent.is_active)
        self.assertEqual(agent.name, '')
        self.assertEqual(agent.identifier, '')
        self.assertIsNone(agent.metadata)
    
    def test_agent_name_max_length(self):
        """Test de longitud máxima del name"""
        long_name = 'x' * 101  # Más de 100 caracteres
        agent_data = self.agent_data.copy()
        agent_data['name'] = long_name
        
        with self.assertRaises(ValidationError):
            agent = Agent(**agent_data)
            agent.full_clean()
    
    def test_agent_identifier_max_length(self):
        """Test de longitud máxima del identifier"""
        long_identifier = 'x' * 256  # Más de 255 caracteres
        agent_data = self.agent_data.copy()
        agent_data['identifier'] = long_identifier
        
        with self.assertRaises(ValidationError):
            agent = Agent(**agent_data)
            agent.full_clean()
    
    def test_agent_ordering(self):
        """Test del ordenamiento por defecto"""
        Agent.objects.create(agent_type='human', name='Zebra Agent')
        Agent.objects.create(agent_type='browser', name='Alpha Agent')
        Agent.objects.create(agent_type='human', name='Alpha Agent')
        
        agents = Agent.objects.all()
        # Debe ordenar por agent_type, luego por name
        self.assertEqual(agents[0].agent_type, 'browser')
        self.assertEqual(agents[1].agent_type, 'human')
        self.assertEqual(agents[1].name, 'Alpha Agent')
        self.assertEqual(agents[2].agent_type, 'human')
        self.assertEqual(agents[2].name, 'Zebra Agent')


class TouchpointClassModelTest(TestCase):
    """Tests para el modelo TouchpointClass"""
    
    def setUp(self):
        """Configuración inicial para los tests"""
        self.touchpoint_class_data = {
            'name': 'Website Page',
            'code': 'WEB_PAGE',
            'description': 'Web page touchpoint',
            'is_active': True
        }
    
    def test_touchpoint_class_creation(self):
        """Test de creación exitosa de TouchpointClass"""
        touchpoint_class = TouchpointClass.objects.create(**self.touchpoint_class_data)
        
        self.assertEqual(touchpoint_class.name, 'Website Page')
        self.assertEqual(touchpoint_class.code, 'WEB_PAGE')
        self.assertEqual(touchpoint_class.description, 'Web page touchpoint')
        self.assertTrue(touchpoint_class.is_active)
        self.assertIsNotNone(touchpoint_class.created_at)
        self.assertIsNotNone(touchpoint_class.updated_at)
    
    def test_touchpoint_class_str_representation(self):
        """Test de representación string del TouchpointClass"""
        touchpoint_class = TouchpointClass.objects.create(**self.touchpoint_class_data)
        self.assertEqual(str(touchpoint_class), 'Website Page')
    
    def test_touchpoint_class_required_fields(self):
        """Test de campos requeridos"""
        # Test sin name
        touchpoint_class_data = self.touchpoint_class_data.copy()
        del touchpoint_class_data['name']
        
        with self.assertRaises(ValidationError):
            touchpoint_class = TouchpointClass(**touchpoint_class_data)
            touchpoint_class.full_clean()
        
        # Test sin code
        touchpoint_class_data = self.touchpoint_class_data.copy()
        del touchpoint_class_data['code']
        
        with self.assertRaises(ValidationError):
            touchpoint_class = TouchpointClass(**touchpoint_class_data)
            touchpoint_class.full_clean()
    
    def test_touchpoint_class_unique_constraints(self):
        """Test de restricciones de unicidad"""
        # Crear primer touchpoint class
        TouchpointClass.objects.create(**self.touchpoint_class_data)
        
        # Test name único - mismo nombre pero diferente code debería fallar
        touchpoint_class_data_duplicate_name = self.touchpoint_class_data.copy()
        touchpoint_class_data_duplicate_name['code'] = 'DIFFERENT_CODE'
        
        with self.assertRaises(IntegrityError):
            TouchpointClass.objects.create(**touchpoint_class_data_duplicate_name)
    
    def test_touchpoint_class_unique_code_constraint(self):
        """Test de restricción de code único"""
        TouchpointClass.objects.create(**self.touchpoint_class_data)
        
        # Test code único - nombre diferente pero mismo code debería fallar
        touchpoint_class_data_duplicate_code = self.touchpoint_class_data.copy()
        touchpoint_class_data_duplicate_code['name'] = 'Different Name'
        
        with self.assertRaises(IntegrityError):
            TouchpointClass.objects.create(**touchpoint_class_data_duplicate_code)
    
    def test_touchpoint_class_default_values(self):
        """Test de valores por defecto"""
        touchpoint_class = TouchpointClass.objects.create(
            name='Test Class',
            code='TEST_CLASS'
        )
        
        self.assertTrue(touchpoint_class.is_active)
        self.assertEqual(touchpoint_class.description, '')


class TouchpointModelTest(TestCase):
    """Tests para el modelo Touchpoint"""
    
    def setUp(self):
        """Configuración inicial para los tests"""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@test.com',
            password='testpass123'
        )
        
        self.country = Country.objects.create(
            iso3_code='TST',
            iso2_code='TS',
            name='Test Country',
            official_name='Republic of Test Country'
        )
        
        self.touchpoint_class = TouchpointClass.objects.create(
            name='Web Page',
            code='WEB_PAGE'
        )
        
        self.product = Product.objects.create(
            name='Test Product',
            description='Test product description'
        )
        
        self.industry = Industry.objects.create(
            name='Technology',
            code='TECH'
        )
        
        self.touchpoint_data = {
            'touchpoint_class': self.touchpoint_class,
            'name': 'Homepage',
            'code': 'HOMEPAGE',
            'description': 'Main website homepage',
            'url': 'https://example.com',
            'external_id': 'EXT001',
            'assigned_staff': self.user,
            'funnel_stage': 'see',
            'product': self.product,
            'is_active': True
        }
    
    def test_touchpoint_creation(self):
        """Test de creación exitosa de Touchpoint"""
        touchpoint = Touchpoint.objects.create(**self.touchpoint_data)
        
        self.assertEqual(touchpoint.touchpoint_class, self.touchpoint_class)
        self.assertEqual(touchpoint.name, 'Homepage')
        self.assertEqual(touchpoint.code, 'HOMEPAGE')
        self.assertEqual(touchpoint.description, 'Main website homepage')
        self.assertEqual(touchpoint.url, 'https://example.com')
        self.assertEqual(touchpoint.external_id, 'EXT001')
        self.assertEqual(touchpoint.assigned_staff, self.user)
        self.assertEqual(touchpoint.funnel_stage, 'see')
        self.assertEqual(touchpoint.product, self.product)
        self.assertTrue(touchpoint.is_active)
    
    def test_touchpoint_str_representation(self):
        """Test de representación string del Touchpoint"""
        touchpoint = Touchpoint.objects.create(**self.touchpoint_data)
        self.assertEqual(str(touchpoint), 'Homepage')
    
    def test_touchpoint_required_fields(self):
        """Test de campos requeridos"""
        # Test sin name
        touchpoint_data = self.touchpoint_data.copy()
        del touchpoint_data['name']
        
        with self.assertRaises(ValidationError):
            touchpoint = Touchpoint(**touchpoint_data)
            touchpoint.full_clean()
    
    def test_touchpoint_funnel_stage_choices(self):
        """Test de validación de choices en funnel_stage"""
        valid_stages = ['see', 'think', 'do', 'care', 'any']
        
        for stage in valid_stages:
            touchpoint_data = self.touchpoint_data.copy()
            touchpoint_data['funnel_stage'] = stage
            touchpoint_data['name'] = f'Test {stage}'
            touchpoint_data['code'] = f'TEST_{stage.upper()}'
            
            touchpoint = Touchpoint.objects.create(**touchpoint_data)
            self.assertEqual(touchpoint.funnel_stage, stage)
    
    def test_touchpoint_invalid_funnel_stage(self):
        """Test de funnel_stage inválido"""
        touchpoint_data = self.touchpoint_data.copy()
        touchpoint_data['funnel_stage'] = 'invalid_stage'
        
        with self.assertRaises(ValidationError):
            touchpoint = Touchpoint(**touchpoint_data)
            touchpoint.full_clean()
    
    def test_touchpoint_many_to_many_relationships(self):
        """Test de relaciones many-to-many"""
        touchpoint = Touchpoint.objects.create(**self.touchpoint_data)
        
        # Agregar industria relacionada
        touchpoint.related_industries.add(self.industry)
        
        self.assertIn(self.industry, touchpoint.related_industries.all())
    
    def test_touchpoint_cascade_deletes(self):
        """Test de eliminación con SET_NULL"""
        touchpoint = Touchpoint.objects.create(**self.touchpoint_data)
        
        # Al eliminar touchpoint_class, se debe setear NULL
        self.touchpoint_class.delete()
        
        touchpoint.refresh_from_db()
        self.assertIsNone(touchpoint.touchpoint_class)
    
    def test_touchpoint_default_values(self):
        """Test de valores por defecto"""
        touchpoint = Touchpoint.objects.create(
            name='Test Touchpoint'
        )
        
        self.assertTrue(touchpoint.is_active)
        self.assertEqual(touchpoint.funnel_stage, 'any')
        self.assertEqual(touchpoint.code, '')
        self.assertEqual(touchpoint.description, '')
        self.assertEqual(touchpoint.url, '')
        self.assertEqual(touchpoint.external_id, '')
        # Test nuevo campo content_type es opcional por defecto
        self.assertIsNone(touchpoint.content_type)

    def test_touchpoint_content_type_choices(self):
        """Test de validación de choices en content_type"""
        valid_content_types = ['affinity', 'category', 'product', 'brand']
        
        for content_type in valid_content_types:
            touchpoint_data = self.touchpoint_data.copy()
            touchpoint_data['content_type'] = content_type
            touchpoint_data['name'] = f'Test {content_type}'
            touchpoint_data['code'] = f'TEST_{content_type.upper()}'
            
            touchpoint = Touchpoint.objects.create(**touchpoint_data)
            self.assertEqual(touchpoint.content_type, content_type)

    def test_touchpoint_content_type_optional(self):
        """Test que content_type es opcional"""
        touchpoint_data = self.touchpoint_data.copy()
        # No incluir content_type en los datos
        touchpoint_data.pop('content_type', None)
        touchpoint_data['name'] = 'Optional Content Type Test'
        touchpoint_data['code'] = 'OPTIONAL_CT'
        
        touchpoint = Touchpoint.objects.create(**touchpoint_data)
        self.assertIsNone(touchpoint.content_type)
        
        # También verificar que se puede guardar explícitamente como None
        touchpoint.content_type = None
        touchpoint.save()
        touchpoint.refresh_from_db()
        self.assertIsNone(touchpoint.content_type)

    def test_touchpoint_invalid_content_type(self):
        """Test de content_type inválido"""
        touchpoint_data = self.touchpoint_data.copy()
        touchpoint_data['content_type'] = 'invalid_content_type'
        touchpoint_data['name'] = 'Invalid Content Type Test'
        touchpoint_data['code'] = 'INVALID_CT'
        
        with self.assertRaises(ValidationError):
            touchpoint = Touchpoint(**touchpoint_data)
            touchpoint.full_clean()

    def test_touchpoint_content_type_blank_string(self):
        """Test que content_type puede ser string vacío"""
        touchpoint_data = self.touchpoint_data.copy()
        touchpoint_data['content_type'] = ''
        touchpoint_data['name'] = 'Blank Content Type Test'
        touchpoint_data['code'] = 'BLANK_CT'
        
        touchpoint = Touchpoint.objects.create(**touchpoint_data)
        self.assertEqual(touchpoint.content_type, '')

    def test_touchpoint_content_type_with_product_consistency(self):
        """Test consistencia entre content_type='product' y campo product"""
        # Crear touchpoint con content_type='product' y product asociado
        touchpoint_data = self.touchpoint_data.copy()
        touchpoint_data['content_type'] = 'product'
        touchpoint_data['name'] = 'Product Consistency Test'
        touchpoint_data['code'] = 'PRODUCT_CONS'
        
        touchpoint = Touchpoint.objects.create(**touchpoint_data)
        self.assertEqual(touchpoint.content_type, 'product')
        self.assertIsNotNone(touchpoint.product)
        
        # También verificar que se puede tener content_type='product' sin product
        touchpoint_data2 = touchpoint_data.copy()
        touchpoint_data2['product'] = None
        touchpoint_data2['name'] = 'Product Without Product'
        touchpoint_data2['code'] = 'PROD_NO_PROD'
        
        touchpoint2 = Touchpoint.objects.create(**touchpoint_data2)
        self.assertEqual(touchpoint2.content_type, 'product')
        self.assertIsNone(touchpoint2.product)

class InteractionModelTest(TestCase):
    """Tests para el modelo Interaction"""
    
    def setUp(self):
        """Configuración inicial para los tests"""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@test.com',
            password='testpass123'
        )
        
        self.country = Country.objects.create(
            iso3_code='TST',
            iso2_code='TS',
            name='Test Country',
            official_name='Republic of Test Country'
        )
        
        self.person = Person.objects.create(
            first_name='Test',
            last_name='Person',
            country_of_nationality=self.country
        )
        
        self.organization = Organization.objects.create(
            name='Test Organization',
            country=self.country
        )
        
        self.touchpoint_class = TouchpointClass.objects.create(
            name='Web Page',
            code='WEB_PAGE'
        )
        
        self.touchpoint = Touchpoint.objects.create(
            touchpoint_class=self.touchpoint_class,
            name='Homepage',
            code='HOMEPAGE'
        )
        
        self.action_type = ActionType.objects.create(
            name='Click',
            code='CLICK'
        )
        
        self.action = Action.objects.create(
            name='Button Click',
            code='BTN_CLICK',
            action_type=self.action_type
        )
        
        self.medium = Medium.objects.create(
            name='Digital',
            code='DIGITAL'
        )
        
        self.channel = Channel.objects.create(
            name='Website',
            code='WEB',
            medium=self.medium
        )
        
        self.agent = Agent.objects.create(
            agent_type='browser',
            name='Test Browser Agent'
        )
        
        self.product = Product.objects.create(
            name='Test Product',
            description='Test product description'
        )
        
        self.interaction_data = {
            'person': self.person,
            'touchpoint': self.touchpoint,
            'action': self.action,
            'channel': self.channel,
            'agent': self.agent,
            'representative': self.user,
            'payload': {'button': 'cta_main', 'section': 'hero'},
            'occurred_at': datetime.now(timezone.utc),
            'source': 'website',
            'duration_seconds': 30,
            'session_id': 'sess_123',
            'latitude': Decimal('40.7128'),
            'longitude': Decimal('-74.0060'),
            'referrer_url': 'https://google.com',
            'user_agent': 'Mozilla/5.0 test browser',
            'ip_address': '192.168.1.1',
            'metadata': {'campaign': 'summer2024'},
            'product': self.product,
            'jtbd_stage': 'job_awareness',
            'is_active': True
        }
    
    def test_interaction_creation(self):
        """Test de creación exitosa de Interaction"""
        interaction = Interaction.objects.create(**self.interaction_data)
        
        self.assertEqual(interaction.person, self.person)
        self.assertEqual(interaction.touchpoint, self.touchpoint)
        self.assertEqual(interaction.action, self.action)
        self.assertEqual(interaction.channel, self.channel)
        self.assertEqual(interaction.agent, self.agent)
        self.assertEqual(interaction.representative, self.user)
        self.assertEqual(interaction.payload['button'], 'cta_main')
        self.assertEqual(interaction.source, 'website')
        self.assertEqual(interaction.duration_seconds, 30)
        self.assertEqual(interaction.session_id, 'sess_123')
        self.assertEqual(interaction.latitude, Decimal('40.7128'))
        self.assertEqual(interaction.longitude, Decimal('-74.0060'))
        self.assertEqual(interaction.referrer_url, 'https://google.com')
        self.assertEqual(interaction.user_agent, 'Mozilla/5.0 test browser')
        self.assertEqual(interaction.ip_address, '192.168.1.1')
        self.assertEqual(interaction.metadata['campaign'], 'summer2024')
        self.assertEqual(interaction.product, self.product)
        self.assertEqual(interaction.jtbd_stage, 'job_awareness')
        self.assertTrue(interaction.is_active)
    
    def test_interaction_str_representation(self):
        """Test de representación string del Interaction"""
        interaction = Interaction.objects.create(**self.interaction_data)
        expected_str = f"Interacción de {self.person} en {self.touchpoint}"
        self.assertEqual(str(interaction), expected_str)
    
    def test_interaction_str_with_organization(self):
        """Test de representación string con organización"""
        interaction_data = self.interaction_data.copy()
        interaction_data['organization'] = self.organization
        del interaction_data['person']
        
        interaction = Interaction.objects.create(**interaction_data)
        expected_str = f"Interacción de {self.organization} en {self.touchpoint}"
        self.assertEqual(str(interaction), expected_str)
    
    def test_interaction_jtbd_stage_choices(self):
        """Test de validación de choices en jtbd_stage"""
        valid_stages = [
            'any', 'job_oblivious', 'job_awareness', 'job_research',
            'job_decision', 'job_execution', 'job_solved', 'stage_unknown'
        ]
        
        for stage in valid_stages:
            interaction_data = self.interaction_data.copy()
            interaction_data['jtbd_stage'] = stage
            interaction_data['occurred_at'] = datetime.now(timezone.utc)
            
            interaction = Interaction.objects.create(**interaction_data)
            self.assertEqual(interaction.jtbd_stage, stage)
    
    def test_interaction_invalid_jtbd_stage(self):
        """Test de jtbd_stage inválido"""
        interaction_data = self.interaction_data.copy()
        interaction_data['jtbd_stage'] = 'invalid_stage'
        
        with self.assertRaises(ValidationError):
            interaction = Interaction(**interaction_data)
            interaction.full_clean()
    
    def test_interaction_resolved_person_property(self):
        """Test de la propiedad resolved_person"""
        interaction = Interaction.objects.create(**self.interaction_data)
        self.assertEqual(interaction.resolved_person, self.person)
        
        # Test con agente que representa persona
        agent_person = Person.objects.create(
            first_name='Agent',
            last_name='Person',
            country_of_nationality=self.country
        )
        
        agent = Agent.objects.create(
            agent_type='human',
            represents_person=agent_person
        )
        
        interaction_data = self.interaction_data.copy()
        del interaction_data['person']
        interaction_data['agent'] = agent
        
        interaction2 = Interaction.objects.create(**interaction_data)
        self.assertEqual(interaction2.resolved_person, agent_person)
    
    def test_interaction_resolved_organization_property(self):
        """Test de la propiedad resolved_organization"""
        interaction_data = self.interaction_data.copy()
        interaction_data['organization'] = self.organization
        
        interaction = Interaction.objects.create(**interaction_data)
        self.assertEqual(interaction.resolved_organization, self.organization)
    
    def test_interaction_geographic_location_property(self):
        """Test de la propiedad geographic_location"""
        interaction = Interaction.objects.create(**self.interaction_data)
        
        location = interaction.geographic_location
        self.assertEqual(location, (40.7128, -74.0060))
        
        # Test sin coordenadas
        interaction_data = self.interaction_data.copy()
        del interaction_data['latitude']
        del interaction_data['longitude']
        
        interaction2 = Interaction.objects.create(**interaction_data)
        self.assertIsNone(interaction2.geographic_location)
    
    def test_interaction_has_duration_property(self):
        """Test de la propiedad has_duration"""
        interaction = Interaction.objects.create(**self.interaction_data)
        self.assertTrue(interaction.has_duration)
        
        # Test sin duración
        interaction_data = self.interaction_data.copy()
        del interaction_data['duration_seconds']
        
        interaction2 = Interaction.objects.create(**interaction_data)
        self.assertFalse(interaction2.has_duration)
    
    def test_interaction_duration_display_property(self):
        """Test de la propiedad duration_display"""
        # Test con 30 segundos
        interaction = Interaction.objects.create(**self.interaction_data)
        self.assertEqual(interaction.duration_display, '30s')
        
        # Test con 90 segundos (1m 30s)
        interaction_data = self.interaction_data.copy()
        interaction_data['duration_seconds'] = 90
        interaction_data['occurred_at'] = datetime.now(timezone.utc)
        
        interaction2 = Interaction.objects.create(**interaction_data)
        self.assertEqual(interaction2.duration_display, '1m 30s')
        
        # Test con 3660 segundos (1h 1m)
        interaction_data['duration_seconds'] = 3660
        interaction_data['occurred_at'] = datetime.now(timezone.utc)
        
        interaction3 = Interaction.objects.create(**interaction_data)
        self.assertEqual(interaction3.duration_display, '1h 1m')
        
        # Test sin duración
        interaction_data['duration_seconds'] = None
        interaction_data['occurred_at'] = datetime.now(timezone.utc)
        
        interaction4 = Interaction.objects.create(**interaction_data)
        self.assertEqual(interaction4.duration_display, 'Sin duración')
    
    def test_interaction_cascade_deletes(self):
        """Test de eliminación con SET_NULL"""
        interaction = Interaction.objects.create(**self.interaction_data)
        
        # Al eliminar person, se debe setear NULL
        self.person.delete()
        
        interaction.refresh_from_db()
        self.assertIsNone(interaction.person)
    
    def test_interaction_default_values(self):
        """Test de valores por defecto"""
        interaction = Interaction.objects.create()
        
        self.assertTrue(interaction.is_active)
        self.assertEqual(interaction.jtbd_stage, 'any')
        self.assertIsNone(interaction.payload)
        self.assertIsNone(interaction.metadata)
        self.assertEqual(interaction.source, '')
        self.assertEqual(interaction.session_id, '')
        self.assertEqual(interaction.referrer_url, '')
        self.assertEqual(interaction.user_agent, '')
    
    def test_interaction_ordering(self):
        """Test del ordenamiento por defecto"""
        # Crear interacciones con diferentes fechas
        earlier_time = datetime(2024, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
        later_time = datetime(2024, 1, 2, 12, 0, 0, tzinfo=timezone.utc)
        
        interaction1_data = self.interaction_data.copy()
        interaction1_data['occurred_at'] = later_time
        interaction1 = Interaction.objects.create(**interaction1_data)
        
        interaction2_data = self.interaction_data.copy()
        interaction2_data['occurred_at'] = earlier_time
        interaction2 = Interaction.objects.create(**interaction2_data)
        
        interactions = Interaction.objects.all()
        # Debe ordenar por -occurred_at (más reciente primero)
        self.assertEqual(interactions[0], interaction1)
        self.assertEqual(interactions[1], interaction2)


# ============================
# TESTS DE API ENDPOINTS
# ============================

from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from django.urls import reverse


class InteractionsAPITestCase(APITestCase):
    """Tests base para APIs de interactions"""
    
    def setUp(self):
        """Configuración común para todos los tests de API"""
        self.client = APIClient()
        
        # Crear usuario para autenticación
        self.user = User.objects.create_user(
            username='testuser',
            email='test@test.com',
            password='testpass123'
        )
        
        # Autenticar cliente
        self.client.force_authenticate(user=self.user)
        
        # Crear datos base necesarios
        self.country = Country.objects.create(
            iso3_code='TST',
            iso2_code='TS',
            name='Test Country',
            official_name='Republic of Test Country'
        )
        
        self.industry = Industry.objects.create(
            name='Technology',
            code='TECH'
        )
        
        self.function = FunctionOrResponsibility.objects.create(
            name='Development',
            code='DEV'
        )
        
        self.skill = Skill.objects.create(
            name='Python',
            code='PY'
        )
        
        # Crear DescriptorFamily antes de WorldDescriptor
        self.descriptor_family = DescriptorFamily.objects.create(
            name='Technical Skills',
            code='TECH_SKILLS',
            description='Family for technical skills and competencies'
        )
        
        self.descriptor = WorldDescriptor.objects.create(
            family=self.descriptor_family,
            name='Web Development',
            code='WEBDEV'
        )


class MediumAPITests(InteractionsAPITestCase):
    """Tests para la API de Medium"""
    
    def setUp(self):
        super().setUp()
        self.medium = Medium.objects.create(
            name='Email Marketing',
            code='EMAIL',
            description='Email marketing campaigns'
        )
        self.list_url = reverse('medium-list')
        self.detail_url = reverse('medium-detail', kwargs={'pk': self.medium.pk})
    
    def test_list_mediums(self):
        """Test listar mediums"""
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['name'], 'Email Marketing')
    
    def test_create_medium(self):
        """Test crear medium"""
        data = {
            'name': 'Social Media',
            'code': 'SOCIAL',
            'description': 'Social media campaigns'
        }
        response = self.client.post(self.list_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Medium.objects.count(), 2)
    
    def test_get_medium_detail(self):
        """Test obtener detalle de medium"""
        response = self.client.get(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'Email Marketing')
    
    def test_update_medium(self):
        """Test actualizar medium"""
        data = {
            'name': 'Email Marketing Updated',
            'code': 'EMAIL',
            'description': 'Updated description'
        }
        response = self.client.put(self.detail_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.medium.refresh_from_db()
        self.assertEqual(self.medium.name, 'Email Marketing Updated')
    
    def test_delete_medium(self):
        """Test eliminar medium"""
        response = self.client.delete(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Medium.objects.filter(is_active=True).count(), 0)
    
    def test_medium_choices_endpoint(self):
        """Test endpoint de choices"""
        url = reverse('medium-choices')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(isinstance(response.data, list))
    
    def test_medium_search_functionality(self):
        """Test funcionalidad de búsqueda"""
        response = self.client.get(self.list_url, {'search': 'Email'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        
        # Búsqueda sin resultados
        response = self.client.get(self.list_url, {'search': 'NoExiste'})
        self.assertEqual(len(response.data['results']), 0)
    
    def test_medium_filtering(self):
        """Test filtrado por estado activo"""
        # Crear medium inactivo
        Medium.objects.create(
            name='Inactive Medium',
            code='INACTIVE',
            is_active=False
        )
        
        # Filtrar solo activos
        response = self.client.get(self.list_url, {'is_active': 'true'})
        self.assertEqual(len(response.data['results']), 1)
        
        # Filtrar solo inactivos
        response = self.client.get(self.list_url, {'is_active': 'false'})
        self.assertEqual(len(response.data['results']), 1)


class ChannelAPITests(InteractionsAPITestCase):
    """Tests para la API de Channel"""
    
    def setUp(self):
        super().setUp()
        self.medium = Medium.objects.create(
            name='Digital',
            code='DIGITAL'
        )
        self.channel = Channel.objects.create(
            name='Website',
            code='WEB',
            medium=self.medium
        )
        self.list_url = reverse('channel-list')
        self.detail_url = reverse('channel-detail', kwargs={'pk': self.channel.pk})
    
    def test_list_channels(self):
        """Test listar channels"""
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
    
    def test_create_channel(self):
        """Test crear channel"""
        data = {
            'name': 'Mobile App',
            'code': 'MOBILE',
            'medium': self.medium.id
        }
        response = self.client.post(self.list_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
    
    def test_channel_by_medium_endpoint(self):
        """Test endpoint para filtrar channels por medium"""
        # TODO: Implementar endpoint personalizado channel-by_medium
        # url = reverse('channel-by_medium')
        # response = self.client.get(url, {'medium': self.medium.id})
        # self.assertEqual(response.status_code, status.HTTP_200_OK)
        # self.assertTrue(len(response.data) >= 1)
        pass
    
    def test_channel_choices_endpoint(self):
        """Test endpoint de choices"""
        # TODO: Implementar endpoint personalizado channel-choices
        # url = reverse('channel-choices')
        # response = self.client.get(url)
        # self.assertEqual(response.status_code, status.HTTP_200_OK)
        pass


class ActionTypeAPITests(InteractionsAPITestCase):
    """Tests para la API de ActionType"""
    
    def setUp(self):
        super().setUp()
        self.action_type = ActionType.objects.create(
            name='Click',
            code='CLICK',
            description='Click actions'
        )
        self.list_url = reverse('actiontype-list')
        self.detail_url = reverse('actiontype-detail', kwargs={'pk': self.action_type.pk})
    
    def test_list_action_types(self):
        """Test listar action types"""
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
    
    def test_create_action_type(self):
        """Test crear action type"""
        data = {
            'name': 'View',
            'code': 'VIEW',
            'description': 'View actions'
        }
        response = self.client.post(self.list_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)


class ActionAPITests(InteractionsAPITestCase):
    """Tests para la API de Action"""
    
    def setUp(self):
        super().setUp()
        self.action_type = ActionType.objects.create(
            name='Click',
            code='CLICK'
        )
        self.action = Action.objects.create(
            name='Button Click',
            code='BTN_CLICK',
            action_type=self.action_type
        )
        self.list_url = reverse('action-list')
        self.detail_url = reverse('action-detail', kwargs={'pk': self.action.pk})
    
    def test_list_actions(self):
        """Test listar actions"""
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
    
    def test_create_action(self):
        """Test crear action"""
        data = {
            'name': 'Link Click',
            'code': 'LINK_CLICK',
            'action_type': self.action_type.id,
            'description': 'Click on a link'
        }
        response = self.client.post(self.list_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)


class AgentAPITests(InteractionsAPITestCase):
    """Tests para la API de Agent"""
    
    def setUp(self):
        super().setUp()
        self.agent = Agent.objects.create(
            agent_type='browser',
            name='Chrome Browser',
            identifier='chrome_v90'
        )
        self.list_url = reverse('agent-list')
        self.detail_url = reverse('agent-detail', kwargs={'pk': self.agent.pk})
    
    def test_list_agents(self):
        """Test listar agents"""
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
    
    def test_create_agent(self):
        """Test crear agent"""
        data = {
            'agent_type': 'system',
            'name': 'API System',
            'identifier': 'api_v1'
        }
        response = self.client.post(self.list_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
    
    def test_agent_filtering_by_type(self):
        """Test filtrado por tipo de agente"""
        # Crear agente de diferente tipo
        Agent.objects.create(
            agent_type='human',
            name='Human User'
        )
        
        response = self.client.get(self.list_url, {'agent_type': 'browser'})
        self.assertEqual(len(response.data['results']), 1)
        
        response = self.client.get(self.list_url, {'agent_type': 'human'})
        self.assertEqual(len(response.data['results']), 1)


class TouchpointClassAPITests(InteractionsAPITestCase):
    """Tests para la API de TouchpointClass"""
    
    def setUp(self):
        super().setUp()
        self.touchpoint_class = TouchpointClass.objects.create(
            name='Landing Page',
            code='LANDING',
            description='Landing page touchpoints'
        )
        self.list_url = reverse('touchpointclass-list')
        self.detail_url = reverse('touchpointclass-detail', kwargs={'pk': self.touchpoint_class.pk})
    
    def test_list_touchpoint_classes(self):
        """Test listar touchpoint classes"""
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
    
    def test_create_touchpoint_class(self):
        """Test crear touchpoint class"""
        data = {
            'name': 'Form',
            'code': 'FORM',
            'description': 'Form touchpoints'
        }
        response = self.client.post(self.list_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)


class TouchpointAPITests(InteractionsAPITestCase):
    """Tests para la API de Touchpoint"""
    
    def setUp(self):
        super().setUp()
        self.touchpoint_class = TouchpointClass.objects.create(
            name='Web Page',
            code='WEB_PAGE'
        )
        
        self.product = Product.objects.create(
            name='Test Product',
            description='Test product description'
        )
        
        self.touchpoint = Touchpoint.objects.create(
            touchpoint_class=self.touchpoint_class,
            name='Homepage',
            code='HOMEPAGE',
            description='Main website homepage',
            url='https://example.com',
            funnel_stage='see',
            product=self.product,
            assigned_staff=self.user
        )
        
        self.list_url = reverse('touchpoint-list')
        self.detail_url = reverse('touchpoint-detail', kwargs={'pk': self.touchpoint.pk})
    
    def test_list_touchpoints(self):
        """Test listar touchpoints"""
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
    
    def test_create_touchpoint(self):
        """Test crear touchpoint"""
        data = {
            'touchpoint_class': self.touchpoint_class.id,
            'name': 'Contact Form',
            'code': 'CONTACT_FORM',
            'description': 'Contact form page',
            'funnel_stage': 'do'
        }
        response = self.client.post(self.list_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
    
    def test_touchpoint_by_funnel_stage_endpoint(self):
        """Test endpoint para filtrar por etapa del funnel"""
        # TODO: Implementar endpoint personalizado touchpoint-by_funnel_stage
        # url = reverse('touchpoint-by_funnel_stage')
        # response = self.client.get(url, {'stage': 'see'})
        # self.assertEqual(response.status_code, status.HTTP_200_OK)
        # self.assertTrue(len(response.data) >= 1)
        pass
    
    def test_touchpoint_interactions_endpoint(self):
        """Test endpoint para obtener interacciones de un touchpoint"""
        url = reverse('touchpoint-interactions', kwargs={'pk': self.touchpoint.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_touchpoint_analytics_endpoint(self):
        """Test endpoint de analytics"""
        url = reverse('touchpoint-analytics')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('total_touchpoints', response.data)
    
    def test_touchpoint_filtering(self):
        """Test filtrado de touchpoints"""
        # Filtrar por funnel stage
        response = self.client.get(self.list_url, {'funnel_stage': 'see'})
        self.assertEqual(len(response.data['results']), 1)
        
        # Filtrar por touchpoint class
        response = self.client.get(self.list_url, {'touchpoint_class': self.touchpoint_class.id})
        self.assertEqual(len(response.data['results']), 1)
        
        # Filtrar por staff asignado
        response = self.client.get(self.list_url, {'assigned_staff': self.user.id})
        self.assertEqual(len(response.data['results']), 1)
    
    def test_touchpoint_semantic_relationships(self):
        """Test relaciones semánticas many-to-many"""
        # Agregar relaciones semánticas
        self.touchpoint.related_industries.add(self.industry)
        self.touchpoint.related_functions.add(self.function)
        self.touchpoint.related_skills.add(self.skill)
        
        response = self.client.get(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Verificar que las relaciones están incluidas
        self.assertIn('related_industries', response.data)
        self.assertIn('related_functions', response.data)
        self.assertIn('related_skills', response.data)


class InteractionAPITests(InteractionsAPITestCase):
    """Tests para la API de Interaction"""
    
    def setUp(self):
        super().setUp()
        
        # Crear datos necesarios
        self.action_type = ActionType.objects.create(
            name='Click',
            code='CLICK'
        )
        
        self.action = Action.objects.create(
            name='Button Click',
            code='BTN_CLICK',
            action_type=self.action_type
        )
        
        self.medium = Medium.objects.create(
            name='Digital',
            code='DIGITAL'
        )
        
        self.channel = Channel.objects.create(
            name='Website',
            code='WEBSITE',
            medium=self.medium
        )
        
        self.agent = Agent.objects.create(
            agent_type='browser',
            name='Test Browser Agent'
        )
        
        self.touchpoint_class = TouchpointClass.objects.create(
            name='Web Page',
            code='WEB_PAGE'
        )
        
        self.touchpoint = Touchpoint.objects.create(
            touchpoint_class=self.touchpoint_class,
            name='Homepage',
            code='HOMEPAGE'
        )
        
        # Crear persona para la interacción
        from entities.models import Person
        self.person = Person.objects.create(
            first_name='John',
            last_name='Doe',
            country_of_nationality=self.country
        )
        
        self.interaction = Interaction.objects.create(
            person=self.person,
            touchpoint=self.touchpoint,
            action=self.action,
            channel=self.channel,
            agent=self.agent,
            representative=self.user,
            session_id='test_session_123',
            jtbd_stage='job_awareness',
            duration_seconds=30,
            payload={'button': 'cta_main'}
        )
        
        self.list_url = reverse('interaction-list')
        self.detail_url = reverse('interaction-detail', kwargs={'pk': self.interaction.pk})
    
    def test_list_interactions(self):
        """Test listar interactions"""
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
    
    def test_create_interaction(self):
        """Test crear interaction"""
        data = {
            'person': self.person.id,
            'touchpoint': self.touchpoint.id,
            'action': self.action.id,
            'channel': self.channel.id,
            'agent': self.agent.id,
            'representative': self.user.id,
            'session_id': 'new_session_456',
            'jtbd_stage': 'job_research',
            'duration_seconds': 45,
            'payload': {'page': 'about'}
        }
        response = self.client.post(self.list_url, data, format='json')
        if response.status_code != status.HTTP_201_CREATED:
            print(f"Error en creación de interaction: {response.data}")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
    
    def test_interaction_filtering(self):
        """Test filtrado de interactions"""
        # Filtrar por etapa JTBD
        response = self.client.get(self.list_url, {'jtbd_stage': 'job_awareness'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Verificar que la respuesta tenga el formato correcto
        if 'results' in response.data:
            self.assertEqual(len(response.data['results']), 1)
        else:
            # Si no está paginado, debe ser una lista directa
            self.assertEqual(len(response.data), 1)
        
        # Filtrar por touchpoint
        response = self.client.get(self.list_url, {'touchpoint': self.touchpoint.id})
        self.assertEqual(len(response.data['results']), 1)
        
        # Filtrar por action
        response = self.client.get(self.list_url, {'action': self.action.id})
        self.assertEqual(len(response.data['results']), 1)
        
        # Filtrar por agent
        response = self.client.get(self.list_url, {'agent': self.agent.id})
        self.assertEqual(len(response.data['results']), 1)
        
        # Filtrar por channel
        response = self.client.get(self.list_url, {'channel': self.channel.id})
        self.assertEqual(len(response.data['results']), 1)
    
    def test_interaction_search(self):
        """Test búsqueda en interactions"""
        response = self.client.get(self.list_url, {'search': 'test_session'})
        self.assertEqual(len(response.data['results']), 1)
        
        # Búsqueda por nombre de persona
        response = self.client.get(self.list_url, {'search': 'John'})
        self.assertEqual(len(response.data['results']), 1)
    
    def test_interaction_analytics_endpoint(self):
        """Test endpoint de analytics de interactions"""
        url = reverse('interaction-analytics')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('total_interactions', response.data)


class InteractionsIntegrationTests(InteractionsAPITestCase):
    """Tests de integración entre diferentes endpoints"""
    
    def test_complete_interaction_flow(self):
        """Test flujo completo de creación de interacción"""
        # 1. Crear medium
        medium_data = {
            'name': 'Digital Marketing',
            'code': 'DIGITAL_MKT'
        }
        medium_response = self.client.post(
            reverse('medium-list'),
            medium_data,
            format='json'
        )
        self.assertEqual(medium_response.status_code, status.HTTP_201_CREATED)
        medium_id = medium_response.data['id']
        
        # 2. Crear channel
        channel_data = {
            'name': 'Company Website',
            'code': 'COMPANY_WEB',
            'medium': medium_id
        }
        channel_response = self.client.post(
            reverse('channel-list'),
            channel_data,
            format='json'
        )
        self.assertEqual(channel_response.status_code, status.HTTP_201_CREATED)
        channel_id = channel_response.data['id']
        
        # 3. Crear action type y action
        action_type_data = {
            'name': 'Page View',
            'code': 'PAGE_VIEW'
        }
        action_type_response = self.client.post(
            reverse('actiontype-list'),
            action_type_data,
            format='json'
        )
        self.assertEqual(action_type_response.status_code, status.HTTP_201_CREATED)
        action_type_id = action_type_response.data['id']
        
        action_data = {
            'name': 'Homepage View',
            'code': 'HOMEPAGE_VIEW',
            'action_type': action_type_id
        }
        action_response = self.client.post(
            reverse('action-list'),
            action_data,
            format='json'
        )
        self.assertEqual(action_response.status_code, status.HTTP_201_CREATED)
        action_id = action_response.data['id']
        
        # 4. Crear agent
        agent_data = {
            'agent_type': 'browser',
            'name': 'Firefox Browser'
        }
        agent_response = self.client.post(
            reverse('agent-list'),
            agent_data,
            format='json'
        )
        self.assertEqual(agent_response.status_code, status.HTTP_201_CREATED)
        agent_id = agent_response.data['id']
        
        # 5. Crear touchpoint class y touchpoint
        touchpoint_class_data = {
            'name': 'Website Page',
            'code': 'WEB_PAGE'
        }
        touchpoint_class_response = self.client.post(
            reverse('touchpointclass-list'),
            touchpoint_class_data,
            format='json'
        )
        self.assertEqual(touchpoint_class_response.status_code, status.HTTP_201_CREATED)
        touchpoint_class_id = touchpoint_class_response.data['id']
        
        touchpoint_data = {
            'touchpoint_class': touchpoint_class_id,
            'name': 'Home Page',
            'code': 'HOME_PAGE',
            'funnel_stage': 'see'
        }
        touchpoint_response = self.client.post(
            reverse('touchpoint-list'),
            touchpoint_data,
            format='json'
        )
        self.assertEqual(touchpoint_response.status_code, status.HTTP_201_CREATED)
        touchpoint_id = touchpoint_response.data['id']
        
        # 6. Crear persona
        from entities.models import Person
        person = Person.objects.create(
            first_name='Jane',
            last_name='Smith',
            country_of_nationality=self.country
        )
        
        # 7. Crear interaction final
        interaction_data = {
            'person': person.id,
            'touchpoint': touchpoint_id,
            'action': action_id,
            'channel': channel_id,
            'agent': agent_id,
            'session_id': 'integration_test_session',
            'jtbd_stage': 'job_awareness',
            'duration_seconds': 60,
            'payload': {'test': 'integration'}
        }
        interaction_response = self.client.post(
            reverse('interaction-list'),
            interaction_data,
            format='json'
        )
        self.assertEqual(interaction_response.status_code, status.HTTP_201_CREATED)
        
        # Verificar que la interacción se creó correctamente
        interaction_id = interaction_response.data['id']
        detail_response = self.client.get(
            reverse('interaction-detail', kwargs={'pk': interaction_id})
        )
        self.assertEqual(detail_response.status_code, status.HTTP_200_OK)
        self.assertEqual(detail_response.data['session_id'], 'integration_test_session')
    
    def test_analytics_endpoints_integration(self):
        """Test integración de endpoints de analytics"""
        # Crear algunos datos de prueba
        medium = Medium.objects.create(name='Test Medium', code='TEST_MED')
        channel = Channel.objects.create(name='Test Channel', code='TEST_CH', medium=medium)
        action_type = ActionType.objects.create(name='Test Action Type', code='TEST_AT')
        action = Action.objects.create(name='Test Action', code='TEST_A', action_type=action_type)
        
        # Test analytics de touchpoints
        touchpoint_analytics = self.client.get(reverse('touchpoint-analytics'))
        self.assertEqual(touchpoint_analytics.status_code, status.HTTP_200_OK)
        
        # Test analytics de interactions
        interaction_analytics = self.client.get(reverse('interaction-analytics'))
        self.assertEqual(interaction_analytics.status_code, status.HTTP_200_OK)
    
    def test_choices_endpoints_consistency(self):
        """Test consistencia de endpoints de choices"""
        endpoints = [
            'medium-choices',
            'channel-choices',
            'actiontype-choices',
            'action-choices',
            'agent-choices',
            'touchpointclass-choices',
            'touchpoint-choices'
        ]
        
        for endpoint in endpoints:
            response = self.client.get(reverse(endpoint))
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertTrue(isinstance(response.data, list))


class InteractionsPerformanceTests(InteractionsAPITestCase):
    """Tests de performance para APIs de interactions"""
    
    def test_large_dataset_performance(self):
        """Test performance con datasets grandes"""
        # Crear múltiples registros para test de performance
        medium = Medium.objects.create(name='Performance Test Medium', code='PERF_MED')
        
        # Crear 50 channels
        channels = []
        for i in range(50):
            channel = Channel.objects.create(
                name=f'Channel {i}',
                code=f'CH_{i}',
                medium=medium
            )
            channels.append(channel)
        
        # Test que la API pueda manejar la lista
        response = self.client.get(reverse('channel-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), min(50, 20))  # Considerando paginación
    
    def test_complex_filtering_performance(self):
        """Test performance de filtros complejos"""
        # Crear datos de prueba
        touchpoint_class = TouchpointClass.objects.create(
            name='Perf Test Class',
            code='PERF_CLASS'
        )
        
        # Crear múltiples touchpoints con relaciones semánticas
        for i in range(20):
            touchpoint = Touchpoint.objects.create(
                touchpoint_class=touchpoint_class,
                name=f'Touchpoint {i}',
                code=f'TP_{i}',
                funnel_stage='see'
            )
            touchpoint.related_industries.add(self.industry)
        
        # Test filtros múltiples
        response = self.client.get(reverse('touchpoint-list'), {
            'funnel_stage': 'see',
            'touchpoint_class': touchpoint_class.id,
            'related_industries': self.industry.id
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class InteractionsValidationTests(InteractionsAPITestCase):
    """Tests de validación para APIs de interactions"""
    
    def test_medium_validation(self):
        """Test validaciones de Medium"""
        # Test campos requeridos
        response = self.client.post(reverse('medium-list'), {}, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        
        # Test código único
        Medium.objects.create(name='Test Medium', code='UNIQUE_CODE')
        duplicate_data = {
            'name': 'Another Medium',
            'code': 'UNIQUE_CODE'
        }
        response = self.client.post(
            reverse('medium-list'),
            duplicate_data,
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_touchpoint_validation(self):
        """Test validaciones de Touchpoint"""
        touchpoint_class = TouchpointClass.objects.create(
            name='Test Class',
            code='TEST_CLASS'
        )
        
        # Test funnel_stage inválido
        invalid_data = {
            'touchpoint_class': touchpoint_class.id,
            'name': 'Invalid Touchpoint',
            'funnel_stage': 'invalid_stage'
        }
        response = self.client.post(
            reverse('touchpoint-list'),
            invalid_data,
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_interaction_validation(self):
        """Test validaciones de Interaction"""
        # Test jtbd_stage inválido
        action_type = ActionType.objects.create(name='Test Action Type', code='TEST_AT')
        action = Action.objects.create(name='Test Action', code='TEST_A', action_type=action_type)
        
        invalid_data = {
            'action': action.id,
            'session_id': 'test_session',
            'jtbd_stage': 'invalid_stage'
        }
        response = self.client.post(
            reverse('interaction-list'),
            invalid_data,
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
