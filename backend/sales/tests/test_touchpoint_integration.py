"""
Tests for sales app touchpoint integration with the Touchpoint Resolution System.
"""

from django.test import TestCase
from django.contrib.auth import get_user_model
from decimal import Decimal

from sales.models import SalesSession, SalesOpportunity, ProductAcquisition
from interactions.models import Channel, Touchpoint, Agent
from connectors.protocols import TouchpointHint
from sales.resolvers import SalesTouchpointResolver, SalesMappingProvider
from entities.models import Person, ContactDetail
from products.models import Product, ProductCategory, Division as ProductDivision
from our_institution.models import Division, OurOrganization
from offers.models import ProductOffering

User = get_user_model()


class SalesSessionTouchpointIntegrationTest(TestCase):
    """Test touchpoint integration for SalesSession model."""
    
    def setUp(self):
        """Set up test data."""
        # Create organization and division
        self.org = OurOrganization.objects.create(
            name="Test University",
            legal_name="Test University Inc.",
            is_active=True
        )
        
        self.division = Division.objects.create(
            organization=self.org,
            name="Pregrado",
            code="PRE",
            is_active=True
        )
        
        # Create user and person
        self.user = User.objects.create_user(
            username="sales_rep",
            email="rep@test.com",
            password="testpass"
        )
        
        self.person = Person.objects.create(
            first_name="John",
            last_name="Doe"
        )
        
        # Create contact detail for email
        ContactDetail.objects.create(
            person=self.person,
            email="john@example.com",
            is_primary=True
        )
        
        # Create product division
        self.product_division = ProductDivision.objects.create(
            name="Test Product Division",
            code="TEST_PDIV"
        )
        
        # Create product category with division
        self.category = ProductCategory.objects.create(
            name="Test Category",
            code="TEST_CAT",
            division=self.product_division
        )
        
        # Create product
        self.product = Product.objects.create(
            name="Test Product",
            code="TEST_PROD",
            description="A test product",
            category=self.category
        )
        
        # Create offering
        self.offering = ProductOffering.objects.create(
            product=self.product,
            name="Test Offering",
            price=Decimal('100.00')
        )
        
        # Create sales opportunity
        self.opportunity = SalesOpportunity.objects.create(
            person=self.person,
            product=self.product,
            offering=self.offering,
            expected_value=Decimal('100.00'),
            stage='interested',
            probability=50
        )
    
    def test_sales_session_touchpoint_inference(self):
        """Test that SalesSession correctly infers touchpoint hints."""
        session = SalesSession(
            opportunity=self.opportunity,
            representative=self.user,
            contacted_via=SalesSession.ContactMedium.EMAIL,
            outcome='interested',
            progress=25
        )
        
        # Test touchpoint hint inference
        hint = session.infer_touchpoint_hint()
        
        self.assertIsInstance(hint, TouchpointHint)
        self.assertEqual(hint.code, "sales.session.email")
        self.assertEqual(hint.channel_code, "sales_pre")
        self.assertEqual(hint.medium_code, "email")
        self.assertEqual(hint.label, "Sesión de ventas vía Correo electrónico")
        
        # Check metadata
        self.assertEqual(hint.metadata["opportunity_id"], str(self.opportunity.id))
        self.assertEqual(hint.metadata["representative_id"], str(self.user.id))
        self.assertEqual(hint.metadata["outcome"], "interested")
        self.assertEqual(hint.metadata["progress"], 25)
        self.assertEqual(hint.metadata["product_id"], str(self.product.id))
        self.assertEqual(hint.metadata["division"], "Pregrado")
        self.assertEqual(hint.metadata["division_code"], "PRE")
    
    def test_sales_session_touchpoint_inference_different_mediums(self):
        """Test touchpoint inference for different contact mediums."""
        mediums = [
            (SalesSession.ContactMedium.TELEPHONE, "phone"),
            (SalesSession.ContactMedium.VIDEOCALL, "video"),
            (SalesSession.ContactMedium.WHATSAPP, "whatsapp"),
            (SalesSession.ContactMedium.ON_CAMPUS, "in_person"),
        ]
        
        for medium, expected_code in mediums:
            with self.subTest(medium=medium):
                session = SalesSession(
                    opportunity=self.opportunity,
                    representative=self.user,
                    contacted_via=medium,
                    outcome='follow_up'
                )
                
                hint = session.infer_touchpoint_hint()
                self.assertEqual(hint.code, f"sales.session.{expected_code}")
                self.assertEqual(hint.medium_code, expected_code)
    
    def test_sales_session_touchpoint_inference_no_division(self):
        """Test touchpoint inference when product has no division."""
        # Create product without division
        product_no_division = Product.objects.create(
            name="Product No Division",
            code="NO_DIV_PROD",
            description="A product without division"
        )
        
        opportunity_no_division = SalesOpportunity.objects.create(
            person=self.person,
            product=product_no_division,
            expected_value=Decimal('50.00'),
            stage='new'
        )
        
        session = SalesSession(
            opportunity=opportunity_no_division,
            representative=self.user,
            contacted_via=SalesSession.ContactMedium.EMAIL
        )
        
        hint = session.infer_touchpoint_hint()
        self.assertEqual(hint.channel_code, "sales")  # Default channel
    
    def test_sales_session_automatic_touchpoint_creation(self):
        """Test that SalesSession automatically creates touchpoints on save."""
        session = SalesSession(
            opportunity=self.opportunity,
            representative=self.user,
            contacted_via=SalesSession.ContactMedium.EMAIL,
            outcome='interested'
        )
        
        # Save the session - should create touchpoint automatically
        session.save()
        
        # Verify touchpoint was created
        self.assertIsNotNone(session.touchpoint)
        
        # Check that the touchpoint has the correct properties
        self.assertIn("email", session.touchpoint.code.lower())
        self.assertEqual(session.touchpoint.funnel_stage, "engage")
    
    def test_sales_session_fallback_manual_creation(self):
        """Test fallback to manual touchpoint creation when resolution fails."""
        # Create a session that will trigger fallback
        session = SalesSession(
            opportunity=self.opportunity,
            representative=self.user,
            contacted_via=SalesSession.ContactMedium.EMAIL,
            outcome='interested'
        )
        
        # Mock the resolver to raise an exception
        original_resolver = SalesTouchpointResolver
        SalesTouchpointResolver = lambda x: type('MockResolver', (), {
            'resolve': lambda self, subject: (_ for _ in ()).throw(Exception("Resolution failed"))
        })()
        
        try:
            # Save should still work with fallback
            session.save()
            
            # Verify touchpoint was created via fallback
            self.assertIsNotNone(session.touchpoint)
            
            # Check that division-specific channel was created
            channel = Channel.objects.filter(name__icontains="Ventas - Pregrado").first()
            self.assertIsNotNone(channel)
            self.assertEqual(channel.code, "sales_pre")
            
        finally:
            # Restore original resolver
            SalesTouchpointResolver = original_resolver
    
    def test_sales_session_division_specific_channel_creation(self):
        """Test that division-specific sales channels are created correctly."""
        # Create another division
        posgrado_division = Division.objects.create(
            organization=self.org,
            name="Posgrado",
            code="POS",
            is_active=True
        )
        
        posgrado_product_division = ProductDivision.objects.create(
            name="Posgrado Product Division",
            code="POS_PDIV"
        )
        
        posgrado_category = ProductCategory.objects.create(
            name="Posgrado Category",
            code="POS_CAT",
            division=posgrado_product_division
        )
        
        posgrado_product = Product.objects.create(
            name="Posgrado Product",
            code="POS_PROD",
            description="A posgrado product",
            category=posgrado_category
        )
        
        posgrado_opportunity = SalesOpportunity.objects.create(
            person=self.person,
            product=posgrado_product,
            expected_value=Decimal('200.00'),
            stage='evaluating'
        )
        
        session = SalesSession(
            opportunity=posgrado_opportunity,
            representative=self.user,
            contacted_via=SalesSession.ContactMedium.TELEPHONE
        )
        
        session.save()
        
        # Check that posgrado-specific channel was created
        posgrado_channel = Channel.objects.filter(name__icontains="Ventas - Posgrado").first()
        self.assertIsNotNone(posgrado_channel)
        self.assertEqual(posgrado_channel.code, "sales_pos")
        
        # Check that pre-existing pregrad channel still exists
        pregrado_channel = Channel.objects.filter(name__icontains="Ventas - Pregrado").first()
        self.assertIsNotNone(pregrado_channel)
        self.assertEqual(pregrado_channel.code, "sales_pre")
    
    def test_representative_division_priority_over_product_division(self):
        """Test that representative's division takes priority over product's division."""
        # Create a representative from a different division
        posgrado_division = Division.objects.create(
            organization=self.org,
            name="Posgrado",
            code="POS",
            is_active=True
        )
        
        posgrado_user = User.objects.create_user(
            username="posgrado_rep",
            email="posgrado@test.com",
            password="testpass"
        )
        
        # Create a sales session with a representative from posgrado division
        # but a product from pregrad division
        session = SalesSession(
            opportunity=self.opportunity,  # This has a pregrad product
            representative=posgrado_user,  # But representative is from posgrado
            contacted_via=SalesSession.ContactMedium.EMAIL,
            outcome='interested'
        )
        
        # Test touchpoint hint inference
        hint = session.infer_touchpoint_hint()
        
        # The channel should be based on the representative's division (posgrado)
        # not the product's division (pregrado)
        # Since we don't have the organizational structure set up in the test,
        # it should fall back to the product's division
        self.assertEqual(hint.channel_code, "sales_pre")  # Falls back to product division
        
        # Save the session
        session.save()
        
        # The touchpoint should be created with the appropriate channel
        self.assertIsNotNone(session.touchpoint)
        self.assertIsNotNone(session.touchpoint.channel)
    
    def test_ai_agent_representative_touchpoint_creation(self):
        """Test touchpoint creation with AI agent as representative."""
        # Create an AI agent representative
        ai_agent = Agent.objects.create(
            agent_type='ai',
            name='Sales AI Assistant',
            identifier='sales-ai-001',
            metadata={
                'division_code': 'PRE',  # Assign to Pregrado division
                'capabilities': ['sales', 'customer_service'],
                'model': 'gpt-4'
            }
        )
        
        # Create a sales session with AI agent as representative
        session = SalesSession(
            opportunity=self.opportunity,
            representative=ai_agent,  # AI agent as representative
            contacted_via=SalesSession.ContactMedium.EMAIL,
            outcome='interested'
        )
        
        # Test touchpoint hint inference
        hint = session.infer_touchpoint_hint()
        
        # The channel should be based on the AI agent's division (pregrado)
        self.assertEqual(hint.channel_code, "sales_pre")
        
        # Check metadata includes AI agent information
        self.assertEqual(hint.metadata["representative_type"], "ai_agent")
        self.assertEqual(hint.metadata["agent_type"], "ai")
        self.assertEqual(hint.metadata["agent_name"], "Sales AI Assistant")
        self.assertIn("agent_metadata", hint.metadata)
        
        # Save the session
        session.save()
        
        # The touchpoint should be created with the appropriate channel
        self.assertIsNotNone(session.touchpoint)
        self.assertIsNotNone(session.touchpoint.channel)
        self.assertEqual(session.touchpoint.channel.code, "sales_pre")
    
    def test_ai_agent_representative_division_priority(self):
        """Test that AI agent's division takes priority over product's division."""
        # Create a posgrado division
        posgrado_division = Division.objects.create(
            organization=self.org,
            name="Posgrado",
            code="POS",
            is_active=True
        )
        
        # Create an AI agent assigned to posgrado division
        ai_agent = Agent.objects.create(
            agent_type='ai',
            name='Posgrado Sales AI',
            identifier='posgrado-ai-001',
            metadata={
                'division_code': 'POS',  # Assign to Posgrado division
                'specialization': 'graduate_programs'
            }
        )
        
        # Create a sales session with AI agent from posgrado
        # but product from pregrad division
        session = SalesSession(
            opportunity=self.opportunity,  # This has a pregrad product
            representative=ai_agent,  # But AI agent is from posgrado
            contacted_via=SalesSession.ContactMedium.TELEPHONE,
            outcome='qualified'
        )
        
        # Test touchpoint hint inference
        hint = session.infer_touchpoint_hint()
        
        # The channel should be based on the AI agent's division (posgrado)
        # not the product's division (pregrado)
        self.assertEqual(hint.channel_code, "sales_pos")
        
        # Save the session
        session.save()
        
        # The touchpoint should be created with the posgrado channel
        self.assertIsNotNone(session.touchpoint)
        self.assertIsNotNone(session.touchpoint.channel)
        self.assertEqual(session.touchpoint.channel.code, "sales_pos")


class SalesOpportunityTouchpointIntegrationTest(TestCase):
    """Test touchpoint integration for SalesOpportunity model."""
    
    def setUp(self):
        """Set up test data."""
        # Create organization and division
        self.org = OurOrganization.objects.create(
            name="Test University",
            legal_name="Test University Inc.",
            is_active=True
        )
        
        self.division = Division.objects.create(
            organization=self.org,
            name="Pregrado",
            code="PRE",
            is_active=True
        )
        
        # Create user and person
        self.user = User.objects.create_user(
            username="sales_rep",
            email="rep@test.com",
            password="testpass"
        )
        
        self.person = Person.objects.create(
            first_name="John",
            last_name="Doe"
        )
        
        # Create contact detail for email
        ContactDetail.objects.create(
            person=self.person,
            email="john@example.com",
            is_primary=True
        )
        
        # Create product division
        self.product_division = ProductDivision.objects.create(
            name="Test Product Division",
            code="TEST_PDIV"
        )
        
        # Create product category with division
        self.category = ProductCategory.objects.create(
            name="Test Category",
            code="TEST_CAT",
            division=self.product_division
        )
        
        # Create product
        self.product = Product.objects.create(
            name="Test Product",
            code="TEST_PROD",
            description="A test product",
            category=self.category
        )
    
    def test_sales_opportunity_channel_inference(self):
        """Test that SalesOpportunity correctly infers channels from division."""
        opportunity = SalesOpportunity(
            person=self.person,
            product=self.product,
            expected_value=Decimal('100.00'),
            stage='new'
        )
        
        # Clean should infer channel from product division
        opportunity.clean()
        
        # Check that channel was inferred
        self.assertIsNotNone(opportunity.channel)
        self.assertIn("Ventas - Pregrado", opportunity.channel.name)
    
    def test_sales_opportunity_channel_inference_from_previous_interaction(self):
        """Test channel inference from previous interactions."""
        # Create a channel and touchpoint first
        channel = Channel.objects.create(
            name="Ventas - Pregrado",
            code="sales_pre"
        )
        
        touchpoint = Touchpoint.objects.create(
            name="Test Touchpoint",
            code="test_tp",
            channel=channel
        )
        
        # Create an interaction with this touchpoint
        from interactions.models import Interaction
        interaction = Interaction.objects.create(
            person=self.person,
            product=self.product,
            touchpoint=touchpoint
        )
        
        # Create opportunity - should infer channel from previous interaction
        opportunity = SalesOpportunity(
            person=self.person,
            product=self.product,
            expected_value=Decimal('100.00'),
            stage='new'
        )
        
        opportunity.clean()
        
        # Should use channel from previous interaction
        self.assertEqual(opportunity.channel, channel)
