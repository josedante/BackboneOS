#!/usr/bin/env python
"""
Script para poblar la base de datos con datos de ejemplo para productos
"""
import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from django.db import transaction
from products.models import ProductCategory, Modality, Customization, Product
from world.models import Industry, Skill, MarketSegment, WorldDescriptor, Tag


def create_sample_data():
    """Crear datos de ejemplo para productos"""
    with transaction.atomic():
        print("🚀 Creando datos de ejemplo para productos...")
        
        # 1. Crear categorías de productos
        print("📂 Creando categorías...")
        
        # Categorías principales
        training_cat = ProductCategory.objects.create(
            name="Capacitación y Formación",
            code="TRAINING",
            description="Productos relacionados con capacitación y desarrollo profesional"
        )
        
        consulting_cat = ProductCategory.objects.create(
            name="Consultoría",
            code="CONSULTING", 
            description="Servicios de consultoría empresarial"
        )
        
        tech_cat = ProductCategory.objects.create(
            name="Tecnología",
            code="TECH",
            description="Productos y servicios tecnológicos"
        )
        
        # Subcategorías
        leadership_cat = ProductCategory.objects.create(
            name="Liderazgo",
            code="LEADERSHIP",
            description="Capacitación en liderazgo y gestión",
            parent=training_cat
        )
        
        digital_skills_cat = ProductCategory.objects.create(
            name="Habilidades Digitales", 
            code="DIGITAL_SKILLS",
            description="Capacitación en competencias digitales",
            parent=training_cat
        )
        
        strategy_cat = ProductCategory.objects.create(
            name="Estrategia Empresarial",
            code="STRATEGY",
            description="Consultoría estratégica",
            parent=consulting_cat
        )
        
        # 2. Crear modalidades
        print("📋 Creando modalidades...")
        
        virtual_mod = Modality.objects.create(
            name="Virtual",
            description="Modalidad completamente virtual"
        )
        
        presencial_mod = Modality.objects.create(
            name="Presencial", 
            description="Modalidad presencial"
        )
        
        hibrido_mod = Modality.objects.create(
            name="Híbrido",
            description="Modalidad mixta virtual y presencial"
        )
        
        # 3. Crear tipos de personalización
        print("🎯 Creando tipos de personalización...")
        
        custom_basic = Customization.objects.create(
            name="Básica",
            description="Personalización básica del contenido"
        )
        
        custom_advanced = Customization.objects.create(
            name="Avanzada",
            description="Personalización completa según necesidades específicas"
        )
        
        # 4. Obtener algunas industrias, skills, etc. existentes
        print("🌐 Obteniendo datos del mundo...")
        
        industries = list(Industry.objects.filter(is_active=True)[:5])
        skills = list(Skill.objects.filter(is_active=True)[:10])
        segments = list(MarketSegment.objects.filter(is_active=True)[:3])
        descriptors = list(WorldDescriptor.objects.filter(is_active=True)[:5])
        tags = list(Tag.objects.filter(is_active=True)[:5])
        
        # 5. Crear productos de ejemplo
        print("📦 Creando productos...")
        
        products_data = [
            {
                'name': 'Programa de Liderazgo Ejecutivo',
                'code': 'PLE-001',
                'description': 'Programa integral para desarrollo de competencias de liderazgo en ejecutivos.',
                'category': leadership_cat,
                'duration': 40,
                'base_price': 2500.00,
                'currency_code': 'USD',
                'customization': custom_advanced,
                'modalities': [presencial_mod, hibrido_mod],
                'industries_count': 3,
                'skills_count': 5
            },
            {
                'name': 'Transformación Digital para Empresas',
                'code': 'TDE-001', 
                'description': 'Consultoría especializada en procesos de transformación digital.',
                'category': strategy_cat,
                'duration': 120,
                'base_price': 15000.00,
                'currency_code': 'USD',
                'customization': custom_advanced,
                'modalities': [virtual_mod, presencial_mod],
                'industries_count': 2,
                'skills_count': 7
            },
            {
                'name': 'Curso de Excel Avanzado',
                'code': 'CEA-001',
                'description': 'Capacitación en funciones avanzadas de Microsoft Excel.',
                'category': digital_skills_cat,
                'duration': 16,
                'base_price': 299.00,
                'currency_code': 'USD', 
                'customization': custom_basic,
                'modalities': [virtual_mod],
                'industries_count': 4,
                'skills_count': 3
            },
            {
                'name': 'Workshop de Innovación y Creatividad',
                'code': 'WIC-001',
                'description': 'Taller práctico para fomentar la innovación y creatividad en equipos.',
                'category': training_cat,
                'duration': 8,
                'base_price': 150.00,
                'currency_code': 'USD',
                'customization': custom_basic,
                'modalities': [presencial_mod, hibrido_mod],
                'industries_count': 5,
                'skills_count': 4
            },
            {
                'name': 'Consultoría en Gestión del Cambio',
                'code': 'CGC-001',
                'description': 'Servicio especializado en gestión y acompañamiento de procesos de cambio organizacional.',
                'category': consulting_cat,
                'duration': 80,
                'base_price': 8500.00,
                'currency_code': 'USD',
                'customization': custom_advanced,
                'modalities': [presencial_mod],
                'industries_count': 3,
                'skills_count': 6
            }
        ]
        
        created_products = []
        for product_data in products_data:
            # Extraer datos relacionales
            modalities = product_data.pop('modalities')
            industries_count = product_data.pop('industries_count')
            skills_count = product_data.pop('skills_count')
            
            # Crear producto
            product = Product.objects.create(**product_data)
            
            # Asignar modalidades
            product.modalities.set(modalities)
            
            # Asignar industrias y skills (sample)
            if industries:
                product.related_industries.set(industries[:industries_count])
            if skills:
                product.related_skills.set(skills[:skills_count])
            if segments:
                product.target_segments.set(segments[:2])
            if descriptors:
                product.descriptors.set(descriptors[:3])
            if tags:
                product.tags.set(tags[:3])
                
            created_products.append(product)
            print(f"  ✅ {product.name}")
        
        print(f"\n🎉 ¡Completado! Se crearon:")
        print(f"  📂 {ProductCategory.objects.count()} categorías")
        print(f"  📋 {Modality.objects.count()} modalidades") 
        print(f"  🎯 {Customization.objects.count()} tipos de personalización")
        print(f"  📦 {Product.objects.count()} productos")
        print(f"\n🔗 URLs disponibles:")
        print(f"  🌐 Admin: http://localhost:8000/admin/")
        print(f"  📡 API: http://localhost:8000/api/products/")
        print(f"  📊 Analytics: http://localhost:8000/api/analytics/")


if __name__ == '__main__':
    create_sample_data()
