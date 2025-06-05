#!/usr/bin/env python
"""
Script para enriquecer los datos de productos con más elementos del ecosystem
"""
import os
import sys
import django
from datetime import timedelta

# Configurar Django
sys.path.append('/Users/josedante/Desarrollo/BackboneOS/Proyecto-OpenSource/backend')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from products.models import ProductCategory, Modality, Customization, Product
from world.models import Industry, Skill, MarketSegment


def create_additional_data():
    """Crear datos adicionales para enriquecer el ecosystem"""
    
    print("🚀 Creando datos adicionales para el ecosystem de productos...")
    
    # Crear más modalidades
    modalities_data = [
        {
            'name': 'Online Síncrono',
            'code': 'ONLINE_SYNC',
            'description': 'Formación en línea con interacción en tiempo real',
            'is_digital': True,
            'requires_physical_space': False
        },
        {
            'name': 'Online Asíncrono',
            'code': 'ONLINE_ASYNC',
            'description': 'Formación en línea a tu propio ritmo',
            'is_digital': True,
            'requires_physical_space': False
        },
        {
            'name': 'Blended Learning',
            'code': 'BLENDED',
            'description': 'Combinación de modalidades presencial y digital',
            'is_digital': True,
            'requires_physical_space': True
        }
    ]
    
    for mod_data in modalities_data:
        modality, created = Modality.objects.get_or_create(
            code=mod_data['code'],
            defaults=mod_data
        )
        if created:
            print(f"✅ Modalidad creada: {modality.name}")
    
    # Crear más niveles de customización
    customizations_data = [
        {
            'name': 'Básica',
            'code': 'BASIC',
            'description': 'Personalización básica del contenido',
            'complexity_level': 1,
            'estimated_additional_cost': 500.00
        },
        {
            'name': 'Intermedia',
            'code': 'INTERMEDIATE',
            'description': 'Personalización intermedia con adaptaciones específicas',
            'complexity_level': 2,
            'estimated_additional_cost': 1500.00
        }
    ]
    
    for cust_data in customizations_data:
        customization, created = Customization.objects.get_or_create(
            code=cust_data['code'],
            defaults=cust_data
        )
        if created:
            print(f"✅ Nivel de customización creado: {customization.name}")
    
    # Crear más categorías
    categories_data = [
        {
            'name': 'Tecnología e Innovación',
            'code': 'TECH_INNOVATION',
            'description': 'Productos relacionados con tecnología e innovación',
            'parent': None
        },
        {
            'name': 'Desarrollo de Software',
            'code': 'SOFTWARE_DEV',
            'description': 'Capacitación en desarrollo de software',
            'parent_code': 'TECH_INNOVATION'
        },
        {
            'name': 'Gestión de Proyectos',
            'code': 'PROJECT_MGMT',
            'description': 'Metodologías y herramientas de gestión de proyectos',
            'parent': None
        },
        {
            'name': 'Metodologías Ágiles',
            'code': 'AGILE_METHODS',
            'description': 'Scrum, Kanban y otras metodologías ágiles',
            'parent_code': 'PROJECT_MGMT'
        }
    ]
    
    # Crear categorías padre primero
    for cat_data in categories_data:
        if 'parent_code' not in cat_data:
            category, created = ProductCategory.objects.get_or_create(
                code=cat_data['code'],
                defaults={
                    'name': cat_data['name'],
                    'description': cat_data['description'],
                    'parent': cat_data.get('parent')
                }
            )
            if created:
                print(f"✅ Categoría creada: {category.name}")
    
    # Crear categorías hijas
    for cat_data in categories_data:
        if 'parent_code' in cat_data:
            parent = ProductCategory.objects.get(code=cat_data['parent_code'])
            category, created = ProductCategory.objects.get_or_create(
                code=cat_data['code'],
                defaults={
                    'name': cat_data['name'],
                    'description': cat_data['description'],
                    'parent': parent
                }
            )
            if created:
                print(f"✅ Categoría creada: {category.name} (hija de {parent.name})")
    
    # Crear más productos
    products_data = [
        {
            'name': 'Bootcamp de Python Avanzado',
            'code': 'BPA-001',
            'description': 'Programa intensivo de programación en Python para desarrollo web y ciencia de datos.',
            'category_code': 'SOFTWARE_DEV',
            'customization_code': 'INTERMEDIATE',
            'base_price': 3500.00,
            'currency_code': 'USD',
            'duration': timedelta(days=21),
            'target_audience': 'Desarrolladores',
            'modality_codes': ['BLENDED', 'ONLINE_SYNC']
        },
        {
            'name': 'Certificación Scrum Master',
            'code': 'CSM-001',
            'description': 'Preparación y certificación oficial como Scrum Master.',
            'category_code': 'AGILE_METHODS',
            'customization_code': 'BASIC',
            'base_price': 1800.00,
            'currency_code': 'USD',
            'duration': timedelta(days=3),
            'target_audience': 'Project Managers',
            'modality_codes': ['VIRTUAL', 'PRESENCIAL']
        },
        {
            'name': 'Workshop de Design Thinking',
            'code': 'WDT-001',
            'description': 'Taller práctico de metodología Design Thinking para innovación.',
            'category_code': 'TECH_INNOVATION',
            'customization_code': 'ADVANCED',
            'base_price': 800.00,
            'currency_code': 'USD',
            'duration': timedelta(hours=16),
            'target_audience': 'Innovadores',
            'modality_codes': ['PRESENCIAL', 'HIBRIDO']
        },
        {
            'name': 'Programa de Transformación Organizacional',
            'code': 'PTO-001',
            'description': 'Programa integral para liderar cambios organizacionales exitosos.',
            'category_code': 'CONSULTING',
            'customization_code': 'ADVANCED',
            'base_price': 25000.00,
            'currency_code': 'USD',
            'duration': timedelta(days=90),
            'target_audience': 'C-Level',
            'modality_codes': ['HIBRIDO', 'PRESENCIAL']
        }
    ]
    
    # Obtener objetos necesarios
    for product_data in products_data:
        try:
            category = ProductCategory.objects.get(code=product_data['category_code'])
            customization = Customization.objects.get(code=product_data['customization_code'])
            
            product, created = Product.objects.get_or_create(
                code=product_data['code'],
                defaults={
                    'name': product_data['name'],
                    'description': product_data['description'],
                    'category': category,
                    'customization': customization,
                    'base_price': product_data['base_price'],
                    'currency_code': product_data['currency_code'],
                    'duration': product_data['duration'],
                    'target_audience': product_data['target_audience']
                }
            )
            
            if created:
                # Agregar modalidades
                for modality_code in product_data['modality_codes']:
                    try:
                        modality = Modality.objects.get(code=modality_code)
                        product.modalities.add(modality)
                    except Modality.DoesNotExist:
                        print(f"⚠️ Modalidad no encontrada: {modality_code}")
                
                print(f"✅ Producto creado: {product.name}")
        
        except (ProductCategory.DoesNotExist, Customization.DoesNotExist) as e:
            print(f"❌ Error creando producto {product_data['name']}: {e}")
    
    # Crear algunos segmentos de mercado si no existen
    segments_data = [
        {
            'name': 'Startups Tecnológicas',
            'code': 'TECH_STARTUPS',
            'description': 'Empresas emergentes en el sector tecnológico',
            'segment_type': 'business_size'
        },
        {
            'name': 'Grandes Corporaciones',
            'code': 'LARGE_CORP',
            'description': 'Empresas multinacionales y grandes corporaciones',
            'segment_type': 'business_size'
        },
        {
            'name': 'Sector Financiero',
            'code': 'FINANCIAL',
            'description': 'Bancos, fintech y servicios financieros',
            'segment_type': 'industry'
        }
    ]
    
    for segment_data in segments_data:
        segment, created = MarketSegment.objects.get_or_create(
            code=segment_data['code'],
            defaults=segment_data
        )
        if created:
            print(f"✅ Segmento creado: {segment.name}")
    
    # Crear algunas habilidades si no existen
    skills_data = [
        {
            'name': 'Python Programming',
            'code': 'PYTHON',
            'description': 'Lenguaje de programación Python',
            'skill_type': 'technical'
        },
        {
            'name': 'Leadership',
            'code': 'LEADERSHIP',
            'description': 'Habilidades de liderazgo y gestión de equipos',
            'skill_type': 'soft'
        },
        {
            'name': 'Agile Methodologies',
            'code': 'AGILE',
            'description': 'Metodologías ágiles de desarrollo',
            'skill_type': 'methodological'
        },
        {
            'name': 'Design Thinking',
            'code': 'DESIGN_THINKING',
            'description': 'Metodología de innovación centrada en el usuario',
            'skill_type': 'creative'
        }
    ]
    
    for skill_data in skills_data:
        skill, created = Skill.objects.get_or_create(
            code=skill_data['code'],
            defaults=skill_data
        )
        if created:
            print(f"✅ Habilidad creada: {skill.name}")
    
    # Crear algunas industrias si no existen
    industries_data = [
        {
            'name': 'Tecnología',
            'code': 'TECH',
            'description': 'Sector tecnológico y software'
        },
        {
            'name': 'Banca y Finanzas',
            'code': 'FINANCE',
            'description': 'Sector financiero y bancario'
        },
        {
            'name': 'Consultoría',
            'code': 'CONSULTING',
            'description': 'Servicios de consultoría empresarial'
        },
        {
            'name': 'Manufactura',
            'code': 'MANUFACTURING',
            'description': 'Sector manufacturero e industrial'
        }
    ]
    
    for industry_data in industries_data:
        industry, created = Industry.objects.get_or_create(
            code=industry_data['code'],
            defaults=industry_data
        )
        if created:
            print(f"✅ Industria creada: {industry.name}")
    
    print("\n🎉 Datos adicionales creados exitosamente!")
    print("\n📊 Resumen final:")
    print(f"   • Productos: {Product.objects.filter(is_active=True).count()}")
    print(f"   • Categorías: {ProductCategory.objects.filter(is_active=True).count()}")
    print(f"   • Modalidades: {Modality.objects.filter(is_active=True).count()}")
    print(f"   • Niveles de customización: {Customization.objects.filter(is_active=True).count()}")
    print(f"   • Habilidades: {Skill.objects.filter(is_active=True).count()}")
    print(f"   • Industrias: {Industry.objects.filter(is_active=True).count()}")
    print(f"   • Segmentos: {MarketSegment.objects.filter(is_active=True).count()}")
    

if __name__ == '__main__':
    create_additional_data()
