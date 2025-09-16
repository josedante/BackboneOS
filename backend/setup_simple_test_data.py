#!/usr/bin/env python3
"""
Simple Test Data Setup Script for BackboneOS Frontend Development

This script creates essential test data with proper field length constraints.
"""

import os
import sys
import django
from datetime import date, timedelta
from decimal import Decimal

# Configure Django
sys.path.append('/app')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from django.db import transaction
from django.contrib.auth import get_user_model

# Import models
from products.models import Product, ProductCategory, Division, Modality, Customization
from world.models import Country, Industry, Skill, MarketSegment, Tag

User = get_user_model()

def create_users():
    """Create test users"""
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
        }
    ]
    
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

def create_world_data():
    """Create world/reference data with proper field lengths"""
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
            'iso3_code': 'COL',
            'iso2_code': 'CO',
            'name': 'Colombia',
            'official_name': 'Republic of Colombia',
            'phone_code': '+57',
            'currency_code': 'COP',
            'timezone': 'America/Bogota'
        }
    ]
    
    for country_data in countries_data:
        country, created = Country.objects.get_or_create(
            iso3_code=country_data['iso3_code'],
            defaults=country_data
        )
        if created:
            print(f"  ✅ Created country: {country.name}")
    
    # Industries (with codes <= 10 chars)
    industries_data = [
        {'name': 'Technology', 'code': 'TECH', 'description': 'Technology and software'},
        {'name': 'Finance', 'code': 'FINANCE', 'description': 'Banking and financial services'},
        {'name': 'Healthcare', 'code': 'HEALTH', 'description': 'Healthcare services'},
        {'name': 'Education', 'code': 'EDUCATION', 'description': 'Education services'},
    ]
    
    for industry_data in industries_data:
        industry, created = Industry.objects.get_or_create(
            code=industry_data['code'],
            defaults=industry_data
        )
        if created:
            print(f"  ✅ Created industry: {industry.name}")
    
    # Skills (with codes <= 10 chars)
    skills_data = [
        {'name': 'Python', 'code': 'PYTHON', 'description': 'Python programming', 'skill_type': 'TE'},
        {'name': 'JavaScript', 'code': 'JAVASCRIPT', 'description': 'JavaScript programming', 'skill_type': 'TE'},
        {'name': 'Leadership', 'code': 'LEADERSHIP', 'description': 'Leadership skills', 'skill_type': 'LE'},
        {'name': 'Sales', 'code': 'SALES', 'description': 'Sales skills', 'skill_type': 'SO'},
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
        {'name': 'Small Business', 'code': 'SMB', 'description': 'Small businesses', 'segment_type': 'B2B'},
        {'name': 'Enterprise', 'code': 'ENTERPRISE', 'description': 'Large enterprises', 'segment_type': 'B2B'},
        {'name': 'Startups', 'code': 'STARTUPS', 'description': 'Early-stage startups', 'segment_type': 'B2B'},
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
    ]
    
    for tag_data in tags_data:
        tag, created = Tag.objects.get_or_create(
            slug=tag_data['slug'],
            defaults=tag_data
        )
        if created:
            print(f"  ✅ Created tag: {tag.name}")

def create_products_data():
    """Create products data"""
    print("📦 Creating products data...")
    
    # Divisions
    divisions_data = [
        {
            'name': 'Technology',
            'code': 'TECH',
            'description': 'Technology solutions'
        },
        {
            'name': 'Training',
            'code': 'TRAINING',
            'description': 'Training programs'
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
        {
            'name': 'Web Development',
            'code': 'WEB_DEV',
            'division': created_divisions[0],  # Technology
            'parent': None
        },
        {
            'name': 'Data Science',
            'code': 'DATA_SCI',
            'division': created_divisions[0],  # Technology
            'parent': None
        },
        {
            'name': 'Leadership Training',
            'code': 'LEAD_TRAIN',
            'division': created_divisions[1],  # Training
            'parent': None
        }
    ]
    
    created_categories = []
    for category_data in categories_data:
        category, created = ProductCategory.objects.get_or_create(
            code=category_data['code'],
            defaults=category_data
        )
        if created:
            print(f"  ✅ Created category: {category.name}")
        created_categories.append(category)
    
    # Modalities
    modalities_data = [
        {'name': 'Online', 'description': 'Online delivery'},
        {'name': 'In-Person', 'description': 'In-person delivery'},
        {'name': 'Hybrid', 'description': 'Mixed delivery'},
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
        {'name': 'Basic', 'description': 'Basic customization'},
        {'name': 'Standard', 'description': 'Standard customization'},
        {'name': 'Premium', 'description': 'Premium customization'},
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
            'description': 'Comprehensive web development bootcamp',
            'category': created_categories[0],  # Web Development
            'base_price': 3500.00,
            'duration': 120,
            'customization': created_customizations[1],  # Standard
            'modalities': [created_modalities[0], created_modalities[2]]  # Online, Hybrid
        },
        {
            'name': 'Python Data Science Course',
            'code': 'PDS-001',
            'description': 'Data science with Python',
            'category': created_categories[1],  # Data Science
            'base_price': 2800.00,
            'duration': 80,
            'customization': created_customizations[2],  # Premium
            'modalities': [created_modalities[0]]  # Online
        },
        {
            'name': 'Leadership Excellence Program',
            'code': 'LEP-001',
            'description': 'Executive leadership development',
            'category': created_categories[2],  # Leadership Training
            'base_price': 4500.00,
            'duration': 60,
            'customization': created_customizations[1],  # Standard
            'modalities': [created_modalities[1], created_modalities[2]]  # In-Person, Hybrid
        }
    ]
    
    created_products = []
    for product_data in products_data:
        modalities = product_data.pop('modalities')
        
        # Convert duration to timedelta
        product_data_copy = product_data.copy()
        if 'duration' in product_data_copy:
            product_data_copy['duration'] = timedelta(hours=product_data_copy['duration'])
        
        product, created = Product.objects.get_or_create(
            code=product_data['code'],
            defaults=product_data_copy
        )
        
        if created:
            # Add modalities
            product.modalities.set(modalities)
            
            # Add some relationships
            industries = list(Industry.objects.all()[:2])
            skills = list(Skill.objects.all()[:3])
            segments = list(MarketSegment.objects.all()[:2])
            tags = list(Tag.objects.all()[:2])
            
            product.related_industries.set(industries)
            product.related_skills.set(skills)
            product.target_segments.set(segments)
            product.tags.set(tags)
            
            print(f"  ✅ Created product: {product.name}")
        created_products.append(product)
    
    return created_products

def main():
    """Main function"""
    print("=" * 60)
    print("🚀 BACKBONEOS SIMPLE TEST DATA SETUP")
    print("=" * 60)
    
    try:
        with transaction.atomic():
            create_users()
            create_world_data()
            products = create_products_data()
            
            print("\n" + "=" * 60)
            print("✅ TEST DATA CREATED SUCCESSFULLY!")
            print("=" * 60)
            
            # Summary
            print(f"\n📊 DATA SUMMARY:")
            print(f"  👥 Users: {User.objects.count()}")
            print(f"  📦 Products: {Product.objects.count()}")
            print(f"  🌍 Countries: {Country.objects.count()}")
            print(f"  🏭 Industries: {Industry.objects.count()}")
            print(f"  🎯 Skills: {Skill.objects.count()}")
            print(f"  🏷️ Tags: {Tag.objects.count()}")
            
            print(f"\n🔐 TEST CREDENTIALS:")
            print(f"  Username: admin / Password: password123")
            print(f"  Username: manager / Password: password123")
            print(f"  Username: sales / Password: password123")
            
            print(f"\n🌐 API ENDPOINTS READY:")
            print(f"  📦 Products: http://localhost:8000/api/products/")
            print(f"  👥 Users: http://localhost:8000/api/users/")
            print(f"  🌍 World: http://localhost:8000/api/world/")
            
            print(f"\n🎉 Ready for frontend development!")
            print("=" * 60)
            
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        return False
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
