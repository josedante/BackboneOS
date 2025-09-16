"""
Test data factories for BackboneOS project.

This module provides Factory Boy factories for creating test data across all models.
Factories make it easy to create realistic test data with proper relationships
and allow for easy customization of test scenarios.

Usage:
    # Create a simple user
    user = UserFactory()
    
    # Create a user with specific attributes
    admin_user = UserFactory(is_staff=True, is_superuser=True)
    
    # Create multiple users
    users = UserFactory.create_batch(5)
    
    # Create a user with related data
    user_with_profile = UserFactory(profile__bio='Test bio')
"""

import factory
import factory.fuzzy
from django.contrib.auth import get_user_model
from django.utils import timezone
from decimal import Decimal
from datetime import timedelta, date
from faker import Faker

from world.models import (
    Country, Industry, FunctionOrResponsibility, Skill,
    PersonalIDType, OrganizationType, OrganizationalIDType,
    DescriptorFamily, WorldDescriptor, MarketSegment, Tag,
    AcademicDegree, Position, Gender, MaritalStatus
)
from products.models import (
    Division, ProductCategory, Modality, Customization, Product
)
from entities.models import (
    Person, ContactDetail, IndividualProfile, Organization, PhysicalAddress
)
from interactions.models import (
    Interaction, Action, ActionType, Channel, Medium
)
from campaigns.models import Campaign
from offers.models import Offer
from our_institution.models import OurOrganization

User = get_user_model()
fake = Faker()


# =============================================================================
# USER FACTORIES
# =============================================================================

class UserFactory(factory.django.DjangoModelFactory):
    """Factory for creating User instances."""
    
    class Meta:
        model = User
    
    username = factory.Sequence(lambda n: f'user{n}')
    email = factory.LazyAttribute(lambda obj: f'{obj.username}@example.com')
    first_name = factory.Faker('first_name')
    last_name = factory.Faker('last_name')
    is_active = True
    is_staff = False
    is_superuser = False
    
    @factory.post_generation
    def password(self, create, extracted, **kwargs):
        if not create:
            return
        password = extracted or 'testpass123'
        self.set_password(password)


class AdminUserFactory(UserFactory):
    """Factory for creating admin users."""
    
    is_staff = True
    is_superuser = True
    username = factory.Sequence(lambda n: f'admin{n}')


# =============================================================================
# WORLD MODEL FACTORIES
# =============================================================================

class CountryFactory(factory.django.DjangoModelFactory):
    """Factory for creating Country instances."""
    
    class Meta:
        model = Country
    
    iso3_code = factory.Sequence(lambda n: f'C{n:02d}')
    iso2_code = factory.Sequence(lambda n: f'C{n}')
    name = factory.Faker('country')
    official_name = factory.LazyAttribute(lambda obj: f'Republic of {obj.name}')
    phone_code = factory.Faker('numerify', text='+###')
    currency_code = factory.Faker('currency_code')
    timezone = factory.Faker('timezone')


class IndustryFactory(factory.django.DjangoModelFactory):
    """Factory for creating Industry instances."""
    
    class Meta:
        model = Industry
    
    name = factory.Faker('company_suffix')
    code = factory.Sequence(lambda n: f'IND{n:03d}')
    description = factory.Faker('text', max_nb_chars=200)
    ciiu_code = factory.Faker('numerify', text='####')
    display_order = factory.Sequence(lambda n: n)
    is_active = True


class SkillFactory(factory.django.DjangoModelFactory):
    """Factory for creating Skill instances."""
    
    class Meta:
        model = Skill
    
    name = factory.Faker('word')
    code = factory.Sequence(lambda n: f'SK{n:03d}')
    description = factory.Faker('text', max_nb_chars=100)
    skill_type = factory.fuzzy.FuzzyChoice([choice[0] for choice in Skill.SKILL_TYPES])
    typical_level_required = factory.fuzzy.FuzzyChoice([choice[0] for choice in Skill.LEVEL_CHOICES])
    display_order = factory.Sequence(lambda n: n)
    is_active = True


class FunctionOrResponsibilityFactory(factory.django.DjangoModelFactory):
    """Factory for creating FunctionOrResponsibility instances."""
    
    class Meta:
        model = FunctionOrResponsibility
    
    name = factory.Faker('job')
    code = factory.Sequence(lambda n: f'FUNC{n:03d}')
    description = factory.Faker('text', max_nb_chars=150)
    typical_level = factory.fuzzy.FuzzyChoice([choice[0] for choice in FunctionOrResponsibility.LEVEL_CHOICES])
    display_order = factory.Sequence(lambda n: n)
    is_active = True


class PersonalIDTypeFactory(factory.django.DjangoModelFactory):
    """Factory for creating PersonalIDType instances."""
    
    class Meta:
        model = PersonalIDType
    
    name = factory.Faker('word')
    code = factory.Sequence(lambda n: f'ID{n:02d}')
    country = factory.SubFactory(CountryFactory)
    regex_pattern = r'^\d{7,10}$'
    max_length = factory.fuzzy.FuzzyInteger(8, 12)
    min_length = factory.fuzzy.FuzzyInteger(6, 8)
    is_active = True


class OrganizationTypeFactory(factory.django.DjangoModelFactory):
    """Factory for creating OrganizationType instances."""
    
    class Meta:
        model = OrganizationType
    
    name = factory.Faker('company_suffix')
    code = factory.Sequence(lambda n: f'ORG{n:02d}')
    description = factory.Faker('text', max_nb_chars=100)
    ownership_type = factory.fuzzy.FuzzyChoice([choice[0] for choice in OrganizationType.OWNERSHIP_CHOICES])
    typical_size = factory.fuzzy.FuzzyChoice([choice[0] for choice in OrganizationType.SIZE_CHOICES])
    display_order = factory.Sequence(lambda n: n)
    is_active = True


class OrganizationalIDTypeFactory(factory.django.DjangoModelFactory):
    """Factory for creating OrganizationalIDType instances."""
    
    class Meta:
        model = OrganizationalIDType
    
    name = factory.Faker('word')
    code = factory.Sequence(lambda n: f'ORGID{n:02d}')
    country = factory.SubFactory(CountryFactory)
    regex_pattern = r'^\d{9,12}$'
    max_length = factory.fuzzy.FuzzyInteger(10, 15)
    min_length = factory.fuzzy.FuzzyInteger(8, 10)
    is_active = True


class DescriptorFamilyFactory(factory.django.DjangoModelFactory):
    """Factory for creating DescriptorFamily instances."""
    
    class Meta:
        model = DescriptorFamily
    
    name = factory.Faker('word')
    code = factory.Sequence(lambda n: f'FAM{n:03d}')
    description = factory.Faker('text', max_nb_chars=100)
    is_active = True


class WorldDescriptorFactory(factory.django.DjangoModelFactory):
    """Factory for creating WorldDescriptor instances."""
    
    class Meta:
        model = WorldDescriptor
    
    family = factory.SubFactory(DescriptorFamilyFactory)
    name = factory.Faker('word')
    code = factory.Sequence(lambda n: f'DESC{n:03d}')
    description = factory.Faker('text', max_nb_chars=100)
    is_active = True


class MarketSegmentFactory(factory.django.DjangoModelFactory):
    """Factory for creating MarketSegment instances."""
    
    class Meta:
        model = MarketSegment
    
    name = factory.Faker('word')
    code = factory.Sequence(lambda n: f'SEG{n:03d}')
    description = factory.Faker('text', max_nb_chars=100)
    segment_type = factory.fuzzy.FuzzyChoice([choice[0] for choice in MarketSegment.SEGMENT_TYPES])
    display_order = factory.Sequence(lambda n: n)
    is_active = True


class TagFactory(factory.django.DjangoModelFactory):
    """Factory for creating Tag instances."""
    
    class Meta:
        model = Tag
    
    name = factory.Faker('word')
    slug = factory.LazyAttribute(lambda obj: obj.name.lower().replace(' ', '-'))
    is_active = True


class GenderFactory(factory.django.DjangoModelFactory):
    """Factory for creating Gender instances."""
    
    class Meta:
        model = Gender
    
    name = factory.fuzzy.FuzzyChoice(['Masculino', 'Femenino', 'Otro'])
    code = factory.LazyAttribute(lambda obj: obj.name[0].upper())
    is_active = True


class MaritalStatusFactory(factory.django.DjangoModelFactory):
    """Factory for creating MaritalStatus instances."""
    
    class Meta:
        model = MaritalStatus
    
    name = factory.fuzzy.FuzzyChoice(['Soltero', 'Casado', 'Divorciado', 'Viudo'])
    code = factory.LazyAttribute(lambda obj: obj.name[:2].upper())
    is_active = True


# =============================================================================
# PRODUCTS MODEL FACTORIES
# =============================================================================

class DivisionFactory(factory.django.DjangoModelFactory):
    """Factory for creating Division instances."""
    
    class Meta:
        model = Division
    
    name = factory.Faker('word')
    code = factory.Sequence(lambda n: f'DIV{n:03d}')
    description = factory.Faker('text', max_nb_chars=200)
    is_active = True


class ProductCategoryFactory(factory.django.DjangoModelFactory):
    """Factory for creating ProductCategory instances."""
    
    class Meta:
        model = ProductCategory
    
    name = factory.Faker('word')
    code = factory.Sequence(lambda n: f'CAT{n:03d}')
    description = factory.Faker('text', max_nb_chars=150)
    division = factory.SubFactory(DivisionFactory)
    is_active = True


class ModalityFactory(factory.django.DjangoModelFactory):
    """Factory for creating Modality instances."""
    
    class Meta:
        model = Modality
    
    name = factory.fuzzy.FuzzyChoice(['Presencial', 'Virtual', 'Híbrido'])
    description = factory.Faker('text', max_nb_chars=100)
    is_active = True


class CustomizationFactory(factory.django.DjangoModelFactory):
    """Factory for creating Customization instances."""
    
    class Meta:
        model = Customization
    
    name = factory.Faker('word')
    description = factory.Faker('text', max_nb_chars=100)
    is_active = True


class ProductFactory(factory.django.DjangoModelFactory):
    """Factory for creating Product instances."""
    
    class Meta:
        model = Product
    
    name = factory.Faker('sentence', nb_words=3)
    code = factory.Sequence(lambda n: f'PROD{n:04d}')
    description = factory.Faker('text', max_nb_chars=300)
    category = factory.SubFactory(ProductCategoryFactory)
    customization = factory.SubFactory(CustomizationFactory)
    duration = factory.fuzzy.FuzzyChoice([
        timedelta(hours=1),
        timedelta(hours=8),
        timedelta(days=1),
        timedelta(days=5),
        timedelta(weeks=1)
    ])
    base_price = factory.fuzzy.FuzzyDecimal(100.0, 5000.0, 2)
    currency_code = factory.fuzzy.FuzzyChoice(['PEN', 'USD', 'EUR'])
    canonical_url = factory.Faker('url')
    is_active = True
    
    @factory.post_generation
    def modalities(self, create, extracted, **kwargs):
        if not create:
            return
        if extracted:
            for modality in extracted:
                self.modalities.add(modality)
        else:
            # Add a random modality
            modality = ModalityFactory()
            self.modalities.add(modality)
    
    @factory.post_generation
    def target_segments(self, create, extracted, **kwargs):
        if not create:
            return
        if extracted:
            for segment in extracted:
                self.target_segments.add(segment)
        else:
            # Add a random segment
            segment = MarketSegmentFactory()
            self.target_segments.add(segment)


# =============================================================================
# ENTITIES MODEL FACTORIES
# =============================================================================

class PersonFactory(factory.django.DjangoModelFactory):
    """Factory for creating Person instances."""
    
    class Meta:
        model = Person
    
    first_name = factory.Faker('first_name')
    last_name = factory.Faker('last_name')
    middle_name = factory.Faker('first_name')
    second_last_name = factory.Faker('last_name')
    gender = factory.SubFactory(GenderFactory)
    marital_status = factory.SubFactory(MaritalStatusFactory)
    country_of_nationality = factory.SubFactory(CountryFactory)
    id_type = factory.SubFactory(PersonalIDTypeFactory)
    id_number = factory.Faker('numerify', text='########')
    birthday = factory.Faker('date_of_birth', minimum_age=18, maximum_age=65)
    is_active = True


class ContactDetailFactory(factory.django.DjangoModelFactory):
    """Factory for creating ContactDetail instances."""
    
    class Meta:
        model = ContactDetail
    
    person = factory.SubFactory(PersonFactory)
    email = factory.Faker('email')
    phone = factory.Faker('phone_number')
    is_primary = True


class IndividualProfileFactory(factory.django.DjangoModelFactory):
    """Factory for creating IndividualProfile instances."""
    
    class Meta:
        model = IndividualProfile
    
    person = factory.SubFactory(PersonFactory)
    bio = factory.Faker('text', max_nb_chars=500)
    website = factory.Faker('url')
    linkedin_url = factory.Faker('url')
    github_url = factory.Faker('url')


class OrganizationFactory(factory.django.DjangoModelFactory):
    """Factory for creating Organization instances."""
    
    class Meta:
        model = Organization
    
    name = factory.Faker('company')
    legal_name = factory.LazyAttribute(lambda obj: f'{obj.name} S.A.C.')
    org_type = factory.SubFactory(OrganizationTypeFactory)
    industry = factory.SubFactory(IndustryFactory)
    country = factory.SubFactory(CountryFactory)
    id_type = factory.SubFactory(OrganizationalIDTypeFactory)
    id_number = factory.Faker('numerify', text='###########')
    website = factory.Faker('url')
    is_active = True


class PhysicalAddressFactory(factory.django.DjangoModelFactory):
    """Factory for creating PhysicalAddress instances."""
    
    class Meta:
        model = PhysicalAddress
    
    owner_person = factory.SubFactory(PersonFactory)
    address = factory.Faker('street_address')
    city = factory.Faker('city')
    region_or_state = factory.Faker('state')
    country = factory.SubFactory(CountryFactory)
    zip_code = factory.Faker('postcode')
    is_primary = True


# =============================================================================
# INTERACTIONS MODEL FACTORIES
# =============================================================================

class ActionTypeFactory(factory.django.DjangoModelFactory):
    """Factory for creating ActionType instances."""
    
    class Meta:
        model = ActionType
    
    name = factory.Faker('word')
    description = factory.Faker('text', max_nb_chars=100)
    is_active = True


class ChannelFactory(factory.django.DjangoModelFactory):
    """Factory for creating Channel instances."""
    
    class Meta:
        model = Channel
    
    name = factory.fuzzy.FuzzyChoice(['Email', 'Phone', 'WhatsApp', 'LinkedIn', 'Website'])
    description = factory.Faker('text', max_nb_chars=100)
    is_active = True


class MediumFactory(factory.django.DjangoModelFactory):
    """Factory for creating Medium instances."""
    
    class Meta:
        model = Medium
    
    name = factory.fuzzy.FuzzyChoice(['Digital', 'Physical', 'Virtual', 'Hybrid'])
    description = factory.Faker('text', max_nb_chars=100)
    is_active = True


class ActionFactory(factory.django.DjangoModelFactory):
    """Factory for creating Action instances."""
    
    class Meta:
        model = Action
    
    name = factory.Faker('word')
    description = factory.Faker('text', max_nb_chars=100)
    action_type = factory.SubFactory(ActionTypeFactory)
    is_active = True


class InteractionFactory(factory.django.DjangoModelFactory):
    """Factory for creating Interaction instances."""
    
    class Meta:
        model = Interaction
    
    person = factory.SubFactory(PersonFactory)
    organization = factory.SubFactory(OrganizationFactory)
    action = factory.SubFactory(ActionFactory)
    channel = factory.SubFactory(ChannelFactory)
    medium = factory.SubFactory(MediumFactory)
    description = factory.Faker('text', max_nb_chars=200)
    outcome = factory.fuzzy.FuzzyChoice(['successful', 'unsuccessful', 'pending'])
    scheduled_date = factory.Faker('future_datetime', end_date='+30d')
    actual_date = factory.Faker('date_time_this_year')


# =============================================================================
# CAMPAIGNS MODEL FACTORIES
# =============================================================================

class CampaignFactory(factory.django.DjangoModelFactory):
    """Factory for creating Campaign instances."""
    
    class Meta:
        model = Campaign
    
    name = factory.Faker('sentence', nb_words=3)
    description = factory.Faker('text', max_nb_chars=300)
    start_date = factory.Faker('future_datetime', end_date='+30d')
    end_date = factory.Faker('future_datetime', end_date='+60d')
    budget = factory.fuzzy.FuzzyDecimal(1000.0, 50000.0, 2)
    currency_code = factory.fuzzy.FuzzyChoice(['PEN', 'USD', 'EUR'])
    status = factory.fuzzy.FuzzyChoice(['draft', 'active', 'paused', 'completed', 'cancelled'])
    is_active = True


# =============================================================================
# OFFERS MODEL FACTORIES
# =============================================================================

class OfferFactory(factory.django.DjangoModelFactory):
    """Factory for creating Offer instances."""
    
    class Meta:
        model = Offer
    
    name = factory.Faker('sentence', nb_words=3)
    description = factory.Faker('text', max_nb_chars=300)
    product = factory.SubFactory(ProductFactory)
    organization = factory.SubFactory(OrganizationFactory)
    person = factory.SubFactory(PersonFactory)
    price = factory.fuzzy.FuzzyDecimal(100.0, 10000.0, 2)
    currency_code = factory.fuzzy.FuzzyChoice(['PEN', 'USD', 'EUR'])
    valid_from = factory.Faker('past_datetime', start_date='-30d')
    valid_until = factory.Faker('future_datetime', end_date='+30d')
    status = factory.fuzzy.FuzzyChoice(['draft', 'active', 'expired', 'cancelled'])
    is_active = True


# =============================================================================
# OUR INSTITUTION MODEL FACTORIES
# =============================================================================

class OurOrganizationFactory(factory.django.DjangoModelFactory):
    """Factory for creating OurOrganization instances."""
    
    class Meta:
        model = OurOrganization
    
    name = factory.Faker('company')
    legal_name = factory.LazyAttribute(lambda obj: f'{obj.name} S.A.C.')
    description = factory.Faker('text', max_nb_chars=300)
    website = factory.Faker('url')
    email = factory.Faker('email')
    phone = factory.Faker('phone_number')
    address = factory.Faker('address')
    country = factory.SubFactory(CountryFactory)
    is_active = True


# =============================================================================
# COMPLEX FACTORY RELATIONSHIPS
# =============================================================================

class CompletePersonFactory(PersonFactory):
    """Factory for creating a person with all related data."""
    
    @factory.post_generation
    def contacts(self, create, extracted, **kwargs):
        if not create:
            return
        # Create primary contact
        ContactDetailFactory(person=self, is_primary=True)
        # Create additional contacts
        ContactDetailFactory.create_batch(2, person=self, is_primary=False)
    
    @factory.post_generation
    def profile(self, create, extracted, **kwargs):
        if not create:
            return
        IndividualProfileFactory(person=self)
    
    @factory.post_generation
    def addresses(self, create, extracted, **kwargs):
        if not create:
            return
        PhysicalAddressFactory.create_batch(2, owner_person=self)


class CompleteOrganizationFactory(OrganizationFactory):
    """Factory for creating an organization with all related data."""
    
    @factory.post_generation
    def contacts(self, create, extracted, **kwargs):
        if not create:
            return
        ContactDetailFactory.create_batch(3, organization=self)


class CompleteProductFactory(ProductFactory):
    """Factory for creating a product with all related data."""
    
    @factory.post_generation
    def modalities(self, create, extracted, **kwargs):
        if not create:
            return
        ModalityFactory.create_batch(2)
        for modality in Modality.objects.all()[:2]:
            self.modalities.add(modality)
    
    @factory.post_generation
    def target_segments(self, create, extracted, **kwargs):
        if not create:
            return
        MarketSegmentFactory.create_batch(2)
        for segment in MarketSegment.objects.all()[:2]:
            self.target_segments.add(segment)
    
    @factory.post_generation
    def related_skills(self, create, extracted, **kwargs):
        if not create:
            return
        SkillFactory.create_batch(3)
        for skill in Skill.objects.all()[:3]:
            self.related_skills.add(skill)


# =============================================================================
# BULK DATA FACTORIES
# =============================================================================

class BulkDataFactory:
    """Factory for creating bulk test data."""
    
    @staticmethod
    def create_countries(count=10):
        """Create multiple countries."""
        return CountryFactory.create_batch(count)
    
    @staticmethod
    def create_industries(count=20):
        """Create multiple industries."""
        return IndustryFactory.create_batch(count)
    
    @staticmethod
    def create_skills(count=50):
        """Create multiple skills."""
        return SkillFactory.create_batch(count)
    
    @staticmethod
    def create_products(count=100):
        """Create multiple products."""
        return ProductFactory.create_batch(count)
    
    @staticmethod
    def create_persons(count=200):
        """Create multiple persons."""
        return PersonFactory.create_batch(count)
    
    @staticmethod
    def create_organizations(count=50):
        """Create multiple organizations."""
        return OrganizationFactory.create_batch(count)
    
    @staticmethod
    def create_complete_dataset():
        """Create a complete dataset for testing."""
        countries = BulkDataFactory.create_countries(5)
        industries = BulkDataFactory.create_industries(10)
        skills = BulkDataFactory.create_skills(25)
        products = BulkDataFactory.create_products(50)
        persons = BulkDataFactory.create_persons(100)
        organizations = BulkDataFactory.create_organizations(25)
        
        return {
            'countries': countries,
            'industries': industries,
            'skills': skills,
            'products': products,
            'persons': persons,
            'organizations': organizations,
        }
