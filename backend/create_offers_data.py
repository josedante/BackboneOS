#!/usr/bin/env python
"""
Script para crear datos de prueba para la aplicación offers
"""
import os
import sys
import django
from datetime import date, timedelta
from decimal import Decimal

# Configurar Django
sys.path.append('/app')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from offers.models import ProductOffering
from products.models import Product, ProductCategory, Division
from interactions.models import Channel, Medium
from world.models import Industry, FunctionOrResponsibility, MarketSegment


def create_sample_offers():
    """Crear ofertas de ejemplo"""
    print("🎯 Creando ofertas de ejemplo...")
    
    # Verificar que tengamos productos
    products = Product.objects.filter(is_active=True)[:5]
    if not products:
        print("❌ No hay productos disponibles. Ejecuta primero el script de productos.")
        return
    
    # Verificar que tengamos canales
    channels = Channel.objects.all()[:3]
    
    # Verificar que tengamos industrias
    industries = Industry.objects.all()[:3]
    
    # Verificar que tengamos funciones
    functions = FunctionOrResponsibility.objects.all()[:3]
    
    ofertas_datos = [
        {
            'name': 'Oferta Black Friday - CRM Premium',
            'code': 'BF2024_CRM_PREM',
            'description': 'Descuento especial Black Friday para nuestro sistema CRM Premium con 30% de descuento.',
            'price': Decimal('1400.00'),
            'currency_code': 'USD',
            'valid_from': date.today() - timedelta(days=5),
            'valid_until': date.today() + timedelta(days=25),
            'auto_renew': False,
            'landing_url': 'https://backboneos.com/offers/black-friday-crm',
            'metadata': {
                'campaign': 'black_friday_2024',
                'discount_percentage': 30,
                'priority': 'high'
            }
        },
        {
            'name': 'Consultoría Estratégica - Paquete Anual',
            'code': 'CONS_ESTRATEGICA_2024',
            'description': 'Paquete completo de consultoría estratégica para transformación digital empresarial.',
            'price': Decimal('25000.00'),
            'currency_code': 'USD',
            'valid_from': date.today(),
            'valid_until': date.today() + timedelta(days=365),
            'auto_renew': True,
            'duration_days': 365,
            'landing_url': 'https://backboneos.com/consultoria-estrategica',
            'metadata': {
                'service_type': 'consultoria',
                'duration_months': 12,
                'includes_training': True
            }
        },
        {
            'name': 'Desarrollo Web Premium - Oferta Navideña',
            'code': 'WEB_PREMIUM_XMAS2024',
            'description': 'Desarrollo de sitio web premium con diseño personalizado y optimización SEO.',
            'price': Decimal('8500.00'),
            'currency_code': 'USD',
            'valid_from': date.today() + timedelta(days=10),
            'valid_until': date.today() + timedelta(days=40),
            'auto_renew': False,
            'landing_url': 'https://backboneos.com/web-premium-navidad',
            'metadata': {
                'includes_seo': True,
                'design_revisions': 3,
                'maintenance_months': 6
            }
        },
        {
            'name': 'Capacitación Digital - Modalidad Virtual',
            'code': 'TRAINING_VIRTUAL_2024',
            'description': 'Programa integral de capacitación digital para equipos de trabajo remoto.',
            'price': Decimal('3200.00'),
            'currency_code': 'USD',
            'valid_from': date.today() - timedelta(days=10),
            'valid_until': date.today() + timedelta(days=60),
            'auto_renew': False,
            'duration_days': 90,
            'landing_url': 'https://backboneos.com/training-virtual',
            'metadata': {
                'modality': 'virtual',
                'max_participants': 50,
                'certification_included': True
            }
        },
        {
            'name': 'Análisis de Datos Empresariales - Q1 2025',
            'code': 'DATA_ANALYSIS_Q1_2025',
            'description': 'Servicio completo de análisis de datos con dashboards interactivos y reportes automatizados.',
            'price': Decimal('12800.00'),
            'currency_code': 'USD',
            'valid_from': date.today() + timedelta(days=30),
            'valid_until': date.today() + timedelta(days=120),
            'auto_renew': True,
            'duration_days': 120,
            'landing_url': 'https://backboneos.com/data-analysis-q1',
            'metadata': {
                'includes_dashboard': True,
                'automated_reports': True,
                'data_sources': ['crm', 'erp', 'web_analytics']
            }
        }
    ]
    
    ofertas_creadas = []
    
    for i, oferta_data in enumerate(ofertas_datos):
        # Asignar producto (rotar entre productos disponibles)
        producto = products[i % len(products)]
        oferta_data['product'] = producto
        
        # Crear la oferta
        oferta = ProductOffering.objects.create(**oferta_data)
        
        # Asignar relaciones M2M si existen datos
        if channels:
            # Asignar 1-2 canales aleatoriamente
            oferta.channels.set(channels[:2])
        
        if industries:
            # Asignar 1-2 industrias
            oferta.related_industries.set(industries[:2])
        
        if functions:
            # Asignar 1-2 funciones
            oferta.related_functions.set(functions[:2])
        
        ofertas_creadas.append(oferta)
        print(f"  ✅ Creada: {oferta.name} - {oferta.price_display}")
    
    print(f"\n🎉 {len(ofertas_creadas)} ofertas creadas exitosamente!")
    
    # Mostrar estadísticas
    total_ofertas = ProductOffering.objects.count()
    ofertas_activas = ProductOffering.objects.filter(is_active=True).count()
    ofertas_validas = ProductOffering.objects.filter(
        is_active=True,
        valid_from__lte=date.today(),
        valid_until__gte=date.today()
    ).count()
    
    print(f"\n📊 Estadísticas de ofertas:")
    print(f"  • Total de ofertas: {total_ofertas}")
    print(f"  • Ofertas activas: {ofertas_activas}")
    print(f"  • Ofertas actualmente válidas: {ofertas_validas}")
    
    # Mostrar ofertas por moneda
    from django.db.models import Count
    by_currency = ProductOffering.objects.values('currency_code').annotate(
        count=Count('id')
    ).order_by('-count')
    
    print(f"\n💰 Ofertas por moneda:")
    for currency_data in by_currency:
        print(f"  • {currency_data['currency_code']}: {currency_data['count']} ofertas")
    
    return ofertas_creadas


def test_api_endpoints():
    """Probar endpoints de la API"""
    print(f"\n🔌 Probando endpoints de la API...")
    
    import requests
    base_url = "http://localhost:8000/api/offers"
    
    endpoints = [
        "/offerings/",
        "/offerings/choices/",
        "/offerings/currently_valid/",
        "/offerings/analytics/"
    ]
    
    for endpoint in endpoints:
        try:
            url = f"{base_url}{endpoint}"
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                print(f"  ✅ {endpoint} - Status: {response.status_code}")
            else:
                print(f"  ❌ {endpoint} - Status: {response.status_code}")
        except Exception as e:
            print(f"  ❌ {endpoint} - Error: {str(e)}")


if __name__ == "__main__":
    print("=" * 60)
    print("🚀 CREANDO DATOS DE PRUEBA PARA APP OFFERS")
    print("=" * 60)
    
    try:
        ofertas = create_sample_offers()
        test_api_endpoints()
        
        print(f"\n" + "=" * 60)
        print("✅ DATOS DE PRUEBA CREADOS EXITOSAMENTE")
        print("=" * 60)
        print(f"\n📍 Puedes acceder a la API en:")
        print(f"  • Lista de ofertas: http://localhost:8000/api/offers/offerings/")
        print(f"  • Admin de Django: http://localhost:8000/admin/offers/productoffering/")
        print(f"  • Analytics: http://localhost:8000/api/offers/offerings/analytics/")
        
    except Exception as e:
        print(f"\n❌ Error al crear datos de prueba: {str(e)}")
        import traceback
        traceback.print_exc()
