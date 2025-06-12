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
from world.models import Country, Industry, FunctionOrResponsibility, Skill, WorldDescriptor
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
            fathers_name='Person',
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
            fathers_name='Person',
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
            code='WEBSITE',
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
            fathers_name='Person',
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
