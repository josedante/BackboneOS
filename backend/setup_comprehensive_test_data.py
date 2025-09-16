#!/usr/bin/env python3
"""
Comprehensive Test Data Setup Script for BackboneOS Frontend Development

This script creates all necessary test data to thoroughly test the frontend
features including products, entities, interactions, campaigns, and offers.

Usage:
    python setup_comprehensive_test_data.py

Or from Docker:
    docker-compose exec backend python setup_comprehensive_test_data.py
"""

import os
import sys
import django
import random
from datetime import date, timedelta
from decimal import Decimal
from django.utils import timezone

# Configure Django
sys.path.append('/app')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from django.db import transaction
from django.contrib.auth import get_user_model

# Import all models
from products.models import Product, ProductCategory, Division, Modality, Customization
from entities.models import Person, Organization, ContactDetail, IndividualProfile, PhysicalAddress
from interactions.models import Channel, Medium, ActionType, Action, Agent, TouchpointClass, Touchpoint, Interaction
from campaigns.models import Campaign, CampaignTouchpoint
from offers.models import ProductOffering
from our_institution.models import OurOrganization, Division as OrgDivision, Team
from world.models import (
    Country, Industry, FunctionOrResponsibility, Skill, PersonalIDType, 
    OrganizationalIDType, OrganizationType, DescriptorFamily, WorldDescriptor,
    MarketSegment, Tag, AcademicDegree, Position
)

User = get_user_model()

def create_users():
    """Create test users for authentication"""
    print("👥 Creating test users...")
    
    users_data = [
        {
            'username': 'admin',
            'email': 'admin@backboneos.com',
            'first_name': 'Admin',
            'last_name': 'User',
            'is_staff': True,
            'is_superuser': True
        },
        {
            'username': 'manager',
            'email': 'manager@backboneos.com',
            'first_name': 'Manager',
            'last_name': 'User',
            'is_staff': True
        },
        {
            'username': 'sales',
            'email': 'sales@backboneos.com',
            'first_name': 'Sales',
            'last_name': 'Rep',
            'is_staff': False
        },
        {
            'username': 'marketing',
            'email': 'marketing@backboneos.com',
            'first_name': 'Marketing',
            'last_name': 'Specialist',
            'is_staff': False
        }
    ]
    
    created_users = []
    for user_data in users_data:
        user, created = User.objects.get_or_create(
            username=user_data['username'],
            defaults=user_data
        )
        if created:
            user.set_password('password123')
            user.save()
            print(f"  ✅ Created user: {user.username}")
        else:
            print(f"  📁 User exists: {user.username}")
        created_users.append(user)
    
    return created_users

def create_world_data():
    """Create world/reference data"""
    print("🌍 Creating world/reference data...")
    
    # Countries
    countries_data = [
        {
            'iso3_code': 'USA',
            'iso2_code': 'US',
            'name': 'United States',
            'official_name': 'United States of America',
            'phone_code': '+1',
            'currency_code': 'USD',
            'timezone': 'America/New_York'
        },
        {
            'iso3_code': 'MEX',
            'iso2_code': 'MX',
            'name': 'Mexico',
            'official_name': 'United Mexican States',
            'phone_code': '+52',
            'currency_code': 'MXN',
            'timezone': 'America/Mexico_City'
        },
        {
            'iso3_code': 'CAN',
            'iso2_code': 'CA',
            'name': 'Canada',
            'official_name': 'Canada',
            'phone_code': '+1',
            'currency_code': 'CAD',
            'timezone': 'America/Toronto'
        },
        {
            'iso3_code': 'ESP',
            'iso2_code': 'ES',
            'name': 'Spain',
            'official_name': 'Kingdom of Spain',
            'phone_code': '+34',
            'currency_code': 'EUR',
            'timezone': 'Europe/Madrid'
        },
        {
            'iso3_code': 'COL',
            'iso2_code': 'CO',
            'name': 'Colombia',
            'official_name': 'Republic of Colombia',
            'phone_code': '+57',
            'currency_code': 'COP',
            'timezone': 'America/Bogota'
        },
    ]
    
    for country_data in countries_data:
        country, created = Country.objects.get_or_create(
            iso3_code=country_data['iso3_code'],
            defaults=country_data
        )
        if created:
            print(f"  ✅ Created country: {country.name}")
    
    # Industries
    industries_data = [
        {'name': 'Technology', 'code': 'TECH', 'description': 'Technology and software industry'},
        {'name': 'Finance', 'code': 'FINANCE', 'description': 'Banking and financial services'},
        {'name': 'Healthcare', 'code': 'HEALTH', 'description': 'Healthcare and medical services'},
        {'name': 'Manufacturing', 'code': 'MANUFACT', 'description': 'Manufacturing and production'},
        {'name': 'Retail', 'code': 'RETAIL', 'description': 'Retail and consumer goods'},
        {'name': 'Education', 'code': 'EDUCATION', 'description': 'Education and training services'},
        {'name': 'Consulting', 'code': 'CONSULT', 'description': 'Business consulting services'},
    ]
    
    for industry_data in industries_data:
        industry, created = Industry.objects.get_or_create(
            code=industry_data['code'],
            defaults=industry_data
        )
        if created:
            print(f"  ✅ Created industry: {industry.name}")
    
    # Skills
    skills_data = [
        {'name': 'Python Programming', 'code': 'PYTHON', 'description': 'Python programming language', 'skill_type': 'TE'},
        {'name': 'JavaScript', 'code': 'JAVASCRIPT', 'description': 'JavaScript programming', 'skill_type': 'TE'},
        {'name': 'Project Management', 'code': 'PROJ_MGMT', 'description': 'Project management skills', 'skill_type': 'LE'},
        {'name': 'Leadership', 'code': 'LEADERSHIP', 'description': 'Leadership and team management', 'skill_type': 'LE'},
        {'name': 'Data Analysis', 'code': 'DATA_ANAL', 'description': 'Data analysis and visualization', 'skill_type': 'AN'},
        {'name': 'Digital Marketing', 'code': 'DIG_MKTG', 'description': 'Digital marketing strategies', 'skill_type': 'CR'},
        {'name': 'Sales', 'code': 'SALES', 'description': 'Sales and business development', 'skill_type': 'SO'},
        {'name': 'Design Thinking', 'code': 'DESIGN_TH', 'description': 'Design thinking methodology', 'skill_type': 'CR'},
    ]
    
    for skill_data in skills_data:
        skill, created = Skill.objects.get_or_create(
            code=skill_data['code'],
            defaults=skill_data
        )
        if created:
            print(f"  ✅ Created skill: {skill.name}")
    
    # Market Segments
    segments_data = [
        {'name': 'Small Business', 'code': 'SMB', 'description': 'Small and medium businesses', 'segment_type': 'B2B'},
        {'name': 'Enterprise', 'code': 'ENTERPRISE', 'description': 'Large enterprise companies', 'segment_type': 'B2B'},
        {'name': 'Startups', 'code': 'STARTUPS', 'description': 'Early-stage startups', 'segment_type': 'B2B'},
        {'name': 'Government', 'code': 'GOVERNMENT', 'description': 'Government organizations', 'segment_type': 'B2G'},
        {'name': 'Non-Profit', 'code': 'NONPROFIT', 'description': 'Non-profit organizations', 'segment_type': 'B2G'},
    ]
    
    for segment_data in segments_data:
        segment, created = MarketSegment.objects.get_or_create(
            code=segment_data['code'],
            defaults=segment_data
        )
        if created:
            print(f"  ✅ Created market segment: {segment.name}")
    
    # Tags
    tags_data = [
        {'name': 'Premium', 'slug': 'premium'},
        {'name': 'Popular', 'slug': 'popular'},
        {'name': 'New', 'slug': 'new'},
        {'name': 'Limited', 'slug': 'limited'},
        {'name': 'Certified', 'slug': 'certified'},
    ]
    
    for tag_data in tags_data:
        tag, created = Tag.objects.get_or_create(
            slug=tag_data['slug'],
            defaults=tag_data
        )
        if created:
            print(f"  ✅ Created tag: {tag.name}")

def create_products_data():
    """Create comprehensive products data"""
    print("📦 Creating products data...")
    
    # Divisions
    divisions_data = [
        {
            'name': 'Technology and Development',
            'code': 'TECH',
            'description': 'Technology solutions and software development'
        },
        {
            'name': 'Business Consulting',
            'code': 'CONSULTING',
            'description': 'Strategic business consulting services'
        },
        {
            'name': 'Training and Education',
            'code': 'TRAINING',
            'description': 'Professional training and education programs'
        },
        {
            'name': 'Marketing and Sales',
            'code': 'MARKETING',
            'description': 'Marketing strategies and sales solutions'
        }
    ]
    
    created_divisions = []
    for division_data in divisions_data:
        division, created = Division.objects.get_or_create(
            code=division_data['code'],
            defaults=division_data
        )
        if created:
            print(f"  ✅ Created division: {division.name}")
        created_divisions.append(division)
    
    # Categories
    categories_data = [
        # Technology
        {'name': 'Software Development', 'code': 'SOFTWARE_DEV', 'division_code': 'TECH', 'parent': None},
        {'name': 'Web Development', 'code': 'WEB_DEV', 'division_code': 'TECH', 'parent': 'SOFTWARE_DEV'},
        {'name': 'Mobile Development', 'code': 'MOBILE_DEV', 'division_code': 'TECH', 'parent': 'SOFTWARE_DEV'},
        {'name': 'Data Science', 'code': 'DATA_SCIENCE', 'division_code': 'TECH', 'parent': None},
        
        # Consulting
        {'name': 'Strategic Consulting', 'code': 'STRATEGIC_CONS', 'division_code': 'CONSULTING', 'parent': None},
        {'name': 'Digital Transformation', 'code': 'DIGITAL_TRANS', 'division_code': 'CONSULTING', 'parent': 'STRATEGIC_CONS'},
        {'name': 'Process Improvement', 'code': 'PROCESS_IMPROV', 'division_code': 'CONSULTING', 'parent': None},
        
        # Training
        {'name': 'Technical Training', 'code': 'TECH_TRAINING', 'division_code': 'TRAINING', 'parent': None},
        {'name': 'Leadership Development', 'code': 'LEADERSHIP_DEV', 'division_code': 'TRAINING', 'parent': None},
        {'name': 'Soft Skills', 'code': 'SOFT_SKILLS', 'division_code': 'TRAINING', 'parent': None},
        
        # Marketing
        {'name': 'Digital Marketing', 'code': 'DIGITAL_MARKETING', 'division_code': 'MARKETING', 'parent': None},
        {'name': 'Content Marketing', 'code': 'CONTENT_MARKETING', 'division_code': 'MARKETING', 'parent': 'DIGITAL_MARKETING'},
    ]
    
    created_categories = {}
    for category_data in categories_data:
        division = Division.objects.get(code=category_data['division_code'])
        parent = None
        if category_data['parent']:
            parent = ProductCategory.objects.get(code=category_data['parent'])
        
        category, created = ProductCategory.objects.get_or_create(
            code=category_data['code'],
            defaults={
                'name': category_data['name'],
                'division': division,
                'parent': parent
            }
        )
        if created:
            print(f"  ✅ Created category: {category.name}")
        created_categories[category_data['code']] = category
    
    # Modalities
    modalities_data = [
        {'name': 'Online', 'description': 'Fully online delivery'},
        {'name': 'In-Person', 'description': 'In-person delivery'},
        {'name': 'Hybrid', 'description': 'Mixed online and in-person'},
        {'name': 'Self-Paced', 'description': 'Self-paced learning'},
    ]
    
    created_modalities = []
    for modality_data in modalities_data:
        modality, created = Modality.objects.get_or_create(
            name=modality_data['name'],
            defaults=modality_data
        )
        if created:
            print(f"  ✅ Created modality: {modality.name}")
        created_modalities.append(modality)
    
    # Customizations
    customizations_data = [
        {'name': 'Basic', 'description': 'Basic customization level'},
        {'name': 'Standard', 'description': 'Standard customization level'},
        {'name': 'Premium', 'description': 'Premium customization level'},
    ]
    
    created_customizations = []
    for customization_data in customizations_data:
        customization, created = Customization.objects.get_or_create(
            name=customization_data['name'],
            defaults=customization_data
        )
        if created:
            print(f"  ✅ Created customization: {customization.name}")
        created_customizations.append(customization)
    
    # Products
    products_data = [
        {
            'name': 'Full-Stack Web Development Bootcamp',
            'code': 'FSWD-001',
            'description': 'Comprehensive bootcamp covering frontend and backend web development',
            'category_code': 'WEB_DEV',
            'base_price': 3500.00,
            'duration': 120,
            'modalities': ['Online', 'Hybrid'],
            'customization': 'Standard'
        },
        {
            'name': 'Python Data Science Masterclass',
            'code': 'PDSM-001',
            'description': 'Advanced data science course using Python and machine learning',
            'category_code': 'DATA_SCIENCE',
            'base_price': 2800.00,
            'duration': 80,
            'modalities': ['Online', 'Self-Paced'],
            'customization': 'Premium'
        },
        {
            'name': 'Digital Transformation Consulting',
            'code': 'DTC-001',
            'description': 'Strategic consulting for digital transformation initiatives',
            'category_code': 'DIGITAL_TRANS',
            'base_price': 15000.00,
            'duration': 180,
            'modalities': ['In-Person', 'Hybrid'],
            'customization': 'Premium'
        },
        {
            'name': 'Leadership Excellence Program',
            'code': 'LEP-001',
            'description': 'Executive leadership development program',
            'category_code': 'LEADERSHIP_DEV',
            'base_price': 4500.00,
            'duration': 60,
            'modalities': ['In-Person', 'Hybrid'],
            'customization': 'Standard'
        },
        {
            'name': 'Agile Project Management Certification',
            'code': 'APMC-001',
            'description': 'Certification program for agile project management',
            'category_code': 'TECH_TRAINING',
            'base_price': 1200.00,
            'duration': 40,
            'modalities': ['Online', 'In-Person'],
            'customization': 'Basic'
        },
        {
            'name': 'Digital Marketing Strategy Workshop',
            'code': 'DMSW-001',
            'description': 'Intensive workshop on digital marketing strategies',
            'category_code': 'DIGITAL_MARKETING',
            'base_price': 800.00,
            'duration': 16,
            'modalities': ['Online', 'In-Person'],
            'customization': 'Basic'
        },
        {
            'name': 'Mobile App Development Course',
            'code': 'MADC-001',
            'description': 'Complete course on mobile app development for iOS and Android',
            'category_code': 'MOBILE_DEV',
            'base_price': 2200.00,
            'duration': 100,
            'modalities': ['Online', 'Hybrid'],
            'customization': 'Standard'
        },
        {
            'name': 'Process Optimization Consulting',
            'code': 'POC-001',
            'description': 'Business process analysis and optimization services',
            'category_code': 'PROCESS_IMPROV',
            'base_price': 8500.00,
            'duration': 90,
            'modalities': ['In-Person', 'Hybrid'],
            'customization': 'Premium'
        }
    ]
    
    created_products = []
    for product_data in products_data:
        category = created_categories[product_data['category_code']]
        customization = Customization.objects.get(name=product_data['customization'])
        
        product, created = Product.objects.get_or_create(
            code=product_data['code'],
            defaults={
                'name': product_data['name'],
                'description': product_data['description'],
                'category': category,
                'base_price': product_data['base_price'],
                'duration': timedelta(hours=product_data['duration']),
                'customization': customization,
                'is_active': True
            }
        )
        
        if created:
            # Add modalities
            for modality_name in product_data['modalities']:
                modality = Modality.objects.get(name=modality_name)
                product.modalities.add(modality)
            
            # Add some random relationships
            industries = list(Industry.objects.all()[:3])
            skills = list(Skill.objects.all()[:5])
            segments = list(MarketSegment.objects.all()[:2])
            tags = list(Tag.objects.all()[:3])
            
            product.related_industries.set(industries)
            product.related_skills.set(skills)
            product.target_segments.set(segments)
            product.tags.set(tags)
            
            print(f"  ✅ Created product: {product.name}")
        created_products.append(product)
    
    return created_products

def create_entities_data():
    """Create entities data (people and organizations)"""
    print("👥 Creating entities data...")
    
    # Organizations
    organizations_data = [
        {
            'name': 'TechCorp Solutions',
            'legal_name': 'TechCorp Solutions Inc.',
            'industry': 'Tecnología',
            'main_address': '123 Tech Street, San Francisco, CA',
            'id_number': 'TC001'
        },
        {
            'name': 'StartupXYZ',
            'legal_name': 'StartupXYZ LLC',
            'industry': 'Tecnología',
            'main_address': '456 Innovation Ave, Austin, TX',
            'id_number': 'SX002'
        },
        {
            'name': 'Global Finance Group',
            'legal_name': 'Global Finance Group Corp.',
            'industry': 'Finance',
            'main_address': '789 Wall Street, New York, NY',
            'id_number': 'GF003'
        },
        {
            'name': 'HealthCare Plus',
            'legal_name': 'HealthCare Plus Medical Center',
            'industry': 'Healthcare',
            'main_address': '321 Health Blvd, Boston, MA',
            'id_number': 'HC004'
        },
        {
            'name': 'EduTech Academy',
            'legal_name': 'EduTech Academy Educational Services',
            'industry': 'Education',
            'main_address': '654 Learning Lane, Seattle, WA',
            'id_number': 'ET005'
        }
    ]
    
    created_organizations = []
    for org_data in organizations_data:
        # Get industry by name - with error handling
        try:
            industry = Industry.objects.get(name=org_data['industry'])
        except Industry.DoesNotExist:
            print(f"  ❌ Industry '{org_data['industry']}' not found. Available industries:")
            for ind in Industry.objects.all():
                print(f"    - {ind.name}")
            continue
        
        organization, created = Organization.objects.get_or_create(
            name=org_data['name'],
            defaults={
                'legal_name': org_data['legal_name'],
                'industry': industry,
                'main_address': org_data['main_address'],
                'id_number': org_data['id_number']
            }
        )
        if created:
            print(f"  ✅ Created organization: {organization.name}")
        created_organizations.append(organization)
    
    # People
    people_data = [
        {
            'first_name': 'John',
            'last_name': 'Smith',
            'email': 'john.smith@techcorp.com',
            'position': 'CTO',
            'organization': 'TechCorp Solutions'
        },
        {
            'first_name': 'Sarah',
            'last_name': 'Johnson',
            'email': 'sarah.johnson@startupxyz.com',
            'position': 'CEO',
            'organization': 'StartupXYZ'
        },
        {
            'first_name': 'Michael',
            'last_name': 'Brown',
            'email': 'michael.brown@globalfinance.com',
            'position': 'VP of Technology',
            'organization': 'Global Finance Group'
        },
        {
            'first_name': 'Emily',
            'last_name': 'Davis',
            'email': 'emily.davis@healthcareplus.com',
            'position': 'IT Director',
            'organization': 'HealthCare Plus'
        },
        {
            'first_name': 'David',
            'last_name': 'Wilson',
            'email': 'david.wilson@edutechacademy.com',
            'position': 'Academic Director',
            'organization': 'EduTech Academy'
        },
        {
            'first_name': 'Lisa',
            'last_name': 'Garcia',
            'email': 'lisa.garcia@techcorp.com',
            'position': 'Project Manager',
            'organization': 'TechCorp Solutions'
        },
        {
            'first_name': 'Robert',
            'last_name': 'Martinez',
            'email': 'robert.martinez@startupxyz.com',
            'position': 'Lead Developer',
            'organization': 'StartupXYZ'
        },
        {
            'first_name': 'Jennifer',
            'last_name': 'Anderson',
            'email': 'jennifer.anderson@globalfinance.com',
            'position': 'Business Analyst',
            'organization': 'Global Finance Group'
        }
    ]
    
    created_people = []
    for person_data in people_data:
        try:
            organization = Organization.objects.get(name=person_data['organization'])
        except Organization.DoesNotExist:
            print(f"  ❌ Organization '{person_data['organization']}' not found. Skipping person: {person_data['first_name']} {person_data['last_name']}")
            continue
        
        # Create person using first_name and fathers_name as unique identifier
        person, created = Person.objects.get_or_create(
            first_name=person_data['first_name'],
            last_name=person_data['last_name'],
            defaults={
                'first_name': person_data['first_name'],
                'last_name': person_data['last_name']
            }
        )
        
        if created:
            # Create contact details
            ContactDetail.objects.create(
                person=person,
                email=person_data['email'],
                phone=f'+1-555-{random.randint(100, 999)}-{random.randint(1000, 9999)}',
                is_primary=True
            )
            
            # Create individual profile
            profile = IndividualProfile.objects.create(
                person=person,
                accepts_privacy_policy=True,
                allows_marketing=random.choice([True, False]),
                preferred_contact_medium='EM'  # Email
            )
            
            # Add some random skills and industries
            skills = list(Skill.objects.all()[:3])
            industries = list(Industry.objects.all()[:2])
            profile.skills.set(skills)
            profile.industries.set(industries)
            
            print(f"  ✅ Created person: {person.first_name} {person.last_name}")
        created_people.append(person)
    
    return created_organizations, created_people

def create_interactions_data():
    """Create interactions data"""
    print("💬 Creating interactions data...")
    
    # Channels
    channels_data = [
        {'name': 'Email', 'code': 'EMAIL', 'description': 'Email communication'},
        {'name': 'Phone', 'code': 'PHONE', 'description': 'Phone calls'},
        {'name': 'Website', 'code': 'WEBSITE', 'description': 'Website interactions'},
        {'name': 'Social Media', 'code': 'SOCIAL', 'description': 'Social media platforms'},
        {'name': 'In-Person', 'code': 'IN_PERSON', 'description': 'Face-to-face meetings'},
    ]
    
    created_channels = []
    for channel_data in channels_data:
        channel, created = Channel.objects.get_or_create(
            name=channel_data['name'],
            defaults=channel_data
        )
        if created:
            print(f"  ✅ Created channel: {channel.name}")
        created_channels.append(channel)
    
    # Mediums
    mediums_data = [
        {'name': 'Direct', 'code': 'DIRECT', 'description': 'Direct communication'},
        {'name': 'Marketing', 'code': 'MARKETING', 'description': 'Marketing campaigns'},
        {'name': 'Sales', 'code': 'SALES', 'description': 'Sales activities'},
        {'name': 'Support', 'code': 'SUPPORT', 'description': 'Customer support'},
    ]
    
    created_mediums = []
    for medium_data in mediums_data:
        medium, created = Medium.objects.get_or_create(
            code=medium_data['code'],
            defaults=medium_data
        )
        if created:
            print(f"  ✅ Created medium: {medium.name}")
        created_mediums.append(medium)
    
    # Action Types
    action_types_data = [
        {'name': 'Inquiry', 'code': 'INQUIRY', 'description': 'Customer inquiry'},
        {'name': 'Meeting', 'code': 'MEETING', 'description': 'Scheduled meeting'},
        {'name': 'Proposal', 'code': 'PROPOSAL', 'description': 'Proposal sent'},
        {'name': 'Follow-up', 'code': 'FOLLOW_UP', 'description': 'Follow-up action'},
        {'name': 'Purchase', 'code': 'PURCHASE', 'description': 'Purchase made'},
    ]
    
    created_action_types = []
    for action_type_data in action_types_data:
        action_type, created = ActionType.objects.get_or_create(
            code=action_type_data['code'],
            defaults=action_type_data
        )
        if created:
            print(f"  ✅ Created action type: {action_type.name}")
        created_action_types.append(action_type)
    
    # Agents
    agents_data = [
        {'name': 'Sales Team', 'agent_type': 'human', 'identifier': 'sales_team'},
        {'name': 'Marketing Team', 'agent_type': 'human', 'identifier': 'marketing_team'},
        {'name': 'Support Team', 'agent_type': 'human', 'identifier': 'support_team'},
        {'name': 'System', 'agent_type': 'system', 'identifier': 'automated_system'},
    ]
    
    created_agents = []
    for agent_data in agents_data:
        agent, created = Agent.objects.get_or_create(
            name=agent_data['name'],
            defaults=agent_data
        )
        if created:
            print(f"  ✅ Created agent: {agent.name}")
        created_agents.append(agent)
    
    # Create some sample interactions
    people = list(Person.objects.all())
    if people:
        for i in range(20):
            person = random.choice(people)
            channel = random.choice(created_channels)
            medium = random.choice(created_mediums)
            action_type = random.choice(created_action_types)
            agent = random.choice(created_agents)
            
            interaction = Interaction.objects.create(
                person=person,
                channel=channel,
                agent=agent,
                payload={
                    'description': f"Sample interaction {i+1} with {person.first_name} {person.last_name}",
                    'outcome': 'positive' if random.choice([True, False]) else 'neutral'
                },
                occurred_at=timezone.now(),
                source='test_data_script'
            )
            
            if i < 5:  # Only print first 5
                print(f"  ✅ Created interaction: {interaction.payload['description']}")

def create_campaigns_data():
    """Create campaigns data"""
    print("🎯 Creating campaigns data...")
    
    # First, create or get our organization
    our_org, created = OurOrganization.objects.get_or_create(
        name='BackboneOS',
        defaults={
            'legal_name': 'BackboneOS Solutions Inc.',
            'tax_id': '12345678901'
        }
    )
    if created:
        print(f"  ✅ Created our organization: {our_org.name}")
    
    # Create organizational structure first
    org_division, created = OrgDivision.objects.get_or_create(
        name='Marketing Division',
        defaults={
            'organization': our_org,
            'code': 'MKT',
            'description': 'Marketing and sales division'
        }
    )
    
    team, created = Team.objects.get_or_create(
        name='Digital Marketing Team',
        defaults={
            'division': org_division,
            'description': 'Digital marketing and campaigns team'
        }
    )
    
    # Campaigns
    campaigns_data = [
        {
            'name': 'Q1 2024 Product Launch',
            'code': 'Q1_2024_LAUNCH',
            'description': 'Product launch campaign for Q1 2024',
            'start_date': date.today() - timedelta(days=30),
            'end_date': date.today() + timedelta(days=60),
            'budget': 50000.00,
            'content_type': 'product',
            'funnel_stage': 'see'
        },
        {
            'name': 'Summer Training Promotion',
            'code': 'SUMMER_TRAINING_2024',
            'description': 'Summer promotion for training programs',
            'start_date': date.today() - timedelta(days=15),
            'end_date': date.today() + timedelta(days=45),
            'budget': 25000.00,
            'content_type': 'product',
            'funnel_stage': 'think'
        },
        {
            'name': 'Enterprise Solutions Campaign',
            'code': 'ENTERPRISE_2024',
            'description': 'Targeted campaign for enterprise solutions',
            'start_date': date.today() - timedelta(days=10),
            'end_date': date.today() + timedelta(days=80),
            'budget': 75000.00,
            'content_type': 'product',
            'funnel_stage': 'do'
        }
    ]
    
    created_campaigns = []
    for campaign_data in campaigns_data:
        campaign, created = Campaign.objects.get_or_create(
            code=campaign_data['code'],
            defaults={
                'name': campaign_data['name'],
                'description': campaign_data['description'],
                'start_date': campaign_data['start_date'],
                'end_date': campaign_data['end_date'],
                'budget': campaign_data['budget'],
                'content_type': campaign_data['content_type'],
                'funnel_stage': campaign_data['funnel_stage'],
                'division': org_division,
                'team': team,
                'is_active': True
            }
        )
        if created:
            print(f"  ✅ Created campaign: {campaign.name}")
        created_campaigns.append(campaign)
    
    return created_campaigns

def create_offers_data():
    """Create offers data"""
    print("🎁 Creating offers data...")
    
    products = list(Product.objects.all())
    if not products:
        print("  ⚠️ No products available for offers")
        return []
    
    offers_data = [
        {
            'name': 'Early Bird Discount - Web Development Bootcamp',
            'code': 'EBD_WEB_DEV_2024',
            'description': 'Early bird discount for web development bootcamp',
            'price': 2800.00,
            'valid_from': date.today(),
            'valid_until': date.today() + timedelta(days=30),
            'auto_renew': False
        },
        {
            'name': 'Corporate Training Package',
            'code': 'CORP_TRAINING_2024',
            'description': 'Special package for corporate training programs',
            'price': 12000.00,
            'valid_from': date.today() - timedelta(days=10),
            'valid_until': date.today() + timedelta(days=90),
            'auto_renew': True
        },
        {
            'name': 'Consulting Services Bundle',
            'code': 'CONSULTING_BUNDLE_2024',
            'description': 'Bundle of consulting services with special pricing',
            'price': 20000.00,
            'valid_from': date.today(),
            'valid_until': date.today() + timedelta(days=120),
            'auto_renew': False
        }
    ]
    
    created_offers = []
    for i, offer_data in enumerate(offers_data):
        product = products[i % len(products)]
        
        offer, created = ProductOffering.objects.get_or_create(
            code=offer_data['code'],
            defaults={
                'name': offer_data['name'],
                'description': offer_data['description'],
                'product': product,
                'price': offer_data['price'],
                'currency_code': 'USD',
                'valid_from': offer_data['valid_from'],
                'valid_until': offer_data['valid_until'],
                'auto_renew': offer_data['auto_renew'],
                'is_active': True
            }
        )
        if created:
            print(f"  ✅ Created offer: {offer.name}")
        created_offers.append(offer)
    
    return created_offers

def main():
    """Main function to create all test data"""
    print("=" * 80)
    print("🚀 BACKBONEOS COMPREHENSIVE TEST DATA SETUP")
    print("=" * 80)
    print("This script will create all necessary test data for frontend development")
    print("=" * 80)
    
    try:
        with transaction.atomic():
            # Create all test data
            users = create_users()
            create_world_data()
            products = create_products_data()
            organizations, people = create_entities_data()
            create_interactions_data()
            campaigns = create_campaigns_data()
            offers = create_offers_data()
            
            print("\n" + "=" * 80)
            print("✅ ALL TEST DATA CREATED SUCCESSFULLY!")
            print("=" * 80)
            
            # Summary
            print(f"\n📊 DATA SUMMARY:")
            print(f"  👥 Users: {User.objects.count()}")
            print(f"  📦 Products: {Product.objects.count()}")
            print(f"  🏢 Organizations: {Organization.objects.count()}")
            print(f"  👤 People: {Person.objects.count()}")
            print(f"  💬 Interactions: {Interaction.objects.count()}")
            print(f"  🎯 Campaigns: {Campaign.objects.count()}")
            print(f"  🎁 Offers: {ProductOffering.objects.count()}")
            print(f"  🌍 Industries: {Industry.objects.count()}")
            print(f"  🏷️ Tags: {Tag.objects.count()}")
            print(f"  🎯 Market Segments: {MarketSegment.objects.count()}")
            
            print(f"\n🔐 TEST CREDENTIALS:")
            print(f"  Username: admin / Password: password123")
            print(f"  Username: manager / Password: password123")
            print(f"  Username: sales / Password: password123")
            print(f"  Username: marketing / Password: password123")
            
            print(f"\n🌐 API ENDPOINTS READY:")
            print(f"  📦 Products: http://localhost:8000/api/products/")
            print(f"  👥 Users: http://localhost:8000/api/users/")
            print(f"  🏢 Entities: http://localhost:8000/api/entities/")
            print(f"  💬 Interactions: http://localhost:8000/api/interactions/")
            print(f"  🎯 Campaigns: http://localhost:8000/api/campaigns/")
            print(f"  🎁 Offers: http://localhost:8000/api/offers/")
            print(f"  🌍 World: http://localhost:8000/api/world/")
            
            print(f"\n🎉 Frontend development can now begin!")
            print("=" * 80)
            
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        return False
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
