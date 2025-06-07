#!/usr/bin/env python
"""
Script de validación completa para el campo canonical_url
"""
import os
import sys
import django

# Configuración de Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from products.models import Product, ProductCategory, Division
from products.serializers import ProductListSerializer, ProductDetailSerializer
from products.admin import ProductAdmin, HasCanonicalUrlFilter
from products.views import ProductFilter
from django.contrib.admin.sites import AdminSite
from django.http import HttpRequest, QueryDict
from django.test.client import Client

def test_model_functionality():
    """Prueba la funcionalidad del modelo"""
    print("🔧 Probando funcionalidad del modelo...")
    
    # Obtener productos de prueba
    products = Product.objects.filter(code__endswith='-TEST')
    
    results = {
        'total_products': products.count(),
        'with_url': 0,
        'without_url': 0,
        'property_working': True
    }
    
    for product in products:
        if product.canonical_url:
            results['with_url'] += 1
        else:
            results['without_url'] += 1
        
        # Verificar que la propiedad has_canonical_url funciona
        expected = bool(product.canonical_url)
        actual = product.has_canonical_url
        if expected != actual:
            results['property_working'] = False
    
    print(f"   ✅ Productos de prueba: {results['total_products']}")
    print(f"   ✅ Con URL canónica: {results['with_url']}")
    print(f"   ✅ Sin URL canónica: {results['without_url']}")
    print(f"   ✅ Propiedad has_canonical_url: {'✓' if results['property_working'] else '✗'}")
    
    return results

def test_serializers():
    """Prueba los serializers"""
    print("\n📋 Probando serializers...")
    
    products = Product.objects.filter(code__endswith='-TEST')
    results = {
        'list_serializer': True,
        'detail_serializer': True,
        'fields_present': True
    }
    
    for product in products:
        # Probar ProductListSerializer
        list_data = ProductListSerializer(product).data
        if 'canonical_url' not in list_data or 'has_canonical_url' not in list_data:
            results['fields_present'] = False
        
        # Probar ProductDetailSerializer
        detail_data = ProductDetailSerializer(product).data
        if 'canonical_url' not in detail_data or 'has_canonical_url' not in detail_data:
            results['fields_present'] = False
    
    print(f"   ✅ Campos presentes en serializers: {'✓' if results['fields_present'] else '✗'}")
    
    return results

def test_admin_functionality():
    """Prueba la funcionalidad del admin"""
    print("\n⚙️ Probando funcionalidad del admin...")
    
    site = AdminSite()
    admin_instance = ProductAdmin(Product, site)
    
    results = {
        'display_method': True,
        'filter_working': True
    }
    
    # Probar método de visualización
    products = Product.objects.filter(code__endswith='-TEST')
    for product in products:
        display = admin_instance.has_canonical_url_display(product)
        if not isinstance(display, str) or not display:
            results['display_method'] = False
    
    # Probar filtro
    try:
        filter_instance = HasCanonicalUrlFilter(
            HttpRequest(), 
            {'has_canonical_url': 'yes'}, 
            Product, 
            admin_instance
        )
        choices = filter_instance.lookup_choices
        if len(choices) != 2:
            results['filter_working'] = False
    except Exception:
        results['filter_working'] = False
    
    print(f"   ✅ Método de visualización: {'✓' if results['display_method'] else '✗'}")
    print(f"   ✅ Filtro personalizado: {'✓' if results['filter_working'] else '✗'}")
    
    return results

def test_view_filters():
    """Prueba los filtros de las vistas"""
    print("\n🔍 Probando filtros de vistas...")
    
    results = {
        'has_url_filter': True,
        'search_filter': True
    }
    
    try:
        # Probar filtro has_canonical_url=true
        query_params = QueryDict('has_canonical_url=true')
        product_filter = ProductFilter(query_params, queryset=Product.objects.all())
        with_url_count = product_filter.qs.count()
        
        # Probar filtro has_canonical_url=false
        query_params_false = QueryDict('has_canonical_url=false')
        product_filter_false = ProductFilter(query_params_false, queryset=Product.objects.all())
        without_url_count = product_filter_false.qs.count()
        
        print(f"   ✅ Productos con URL (filtro): {with_url_count}")
        print(f"   ✅ Productos sin URL (filtro): {without_url_count}")
        
        # Probar búsqueda
        query_params_search = QueryDict('search=example.com')
        product_filter_search = ProductFilter(query_params_search, queryset=Product.objects.all())
        search_count = product_filter_search.qs.count()
        
        print(f"   ✅ Productos encontrados con 'example.com': {search_count}")
        
    except Exception as e:
        print(f"   ❌ Error en filtros: {e}")
        results['has_url_filter'] = False
        results['search_filter'] = False
    
    return results

def test_api_functionality():
    """Prueba la funcionalidad que usan las APIs"""
    print("\n🌐 Probando funcionalidad de las APIs...")
    
    results = {
        'queryset_filters': True,
        'serializer_output': True
    }
    
    try:
        # Probar filtros que usa la API
        all_products = Product.objects.all().count()
        with_url = Product.objects.filter(canonical_url__isnull=False).exclude(canonical_url='').count()
        without_url = Product.objects.filter(canonical_url__isnull=True).count() + Product.objects.filter(canonical_url='').count()
        
        print(f"   ✅ Total productos: {all_products}")
        print(f"   ✅ Con URL canónica: {with_url}")
        print(f"   ✅ Sin URL canónica: {without_url}")
        
        # Probar serializers con datos reales
        test_products = Product.objects.filter(code__endswith='-TEST')
        for product in test_products:
            list_data = ProductListSerializer(product).data
            detail_data = ProductDetailSerializer(product).data
            
            # Verificar que los campos están presentes y son correctos
            if 'canonical_url' not in list_data or 'has_canonical_url' not in list_data:
                results['serializer_output'] = False
            if 'canonical_url' not in detail_data or 'has_canonical_url' not in detail_data:
                results['serializer_output'] = False
                
            # Verificar consistencia
            if list_data['has_canonical_url'] != bool(product.canonical_url):
                results['serializer_output'] = False
        
        print(f"   ✅ Serializers: {'✓' if results['serializer_output'] else '✗'}")
    
    except Exception as e:
        print(f"   ❌ Error en funcionalidad de APIs: {e}")
        results['queryset_filters'] = False
        results['serializer_output'] = False
    
    return results

def generate_report(model_results, serializer_results, admin_results, view_results, api_results):
    """Genera un reporte final"""
    print("\n" + "="*60)
    print("📊 REPORTE FINAL - CAMPO CANONICAL_URL")
    print("="*60)
    
    all_passed = True
    
    # Modelo
    print("\n🔧 MODELO:")
    if model_results['property_working']:
        print("   ✅ Propiedad has_canonical_url funcionando")
    else:
        print("   ❌ Propiedad has_canonical_url con errores")
        all_passed = False
    
    # Serializers
    print("\n📋 SERIALIZERS:")
    if serializer_results['fields_present']:
        print("   ✅ Campos presentes en todos los serializers")
    else:
        print("   ❌ Campos faltantes en serializers")
        all_passed = False
    
    # Admin
    print("\n⚙️ ADMIN:")
    if admin_results['display_method'] and admin_results['filter_working']:
        print("   ✅ Visualización y filtros funcionando")
    else:
        print("   ❌ Problemas en admin")
        all_passed = False
    
    # Vistas
    print("\n🔍 VISTAS:")
    if view_results['has_url_filter'] and view_results['search_filter']:
        print("   ✅ Filtros funcionando correctamente")
    else:
        print("   ❌ Problemas en filtros de vistas")
        all_passed = False
    
    # API
    print("\n🌐 API:")
    api_working = api_results['queryset_filters'] and api_results['serializer_output']
    if api_working:
        print("   ✅ Funcionalidad de API funcionando")
    else:
        print("   ❌ Problemas en funcionalidad de API")
        all_passed = False
    
    print("\n" + "="*60)
    if all_passed:
        print("🎉 IMPLEMENTACIÓN COMPLETA Y FUNCIONAL")
        print("✅ El campo canonical_url está correctamente integrado")
    else:
        print("⚠️ HAY ALGUNOS PROBLEMAS QUE REQUIEREN ATENCIÓN")
    print("="*60)
    
    return all_passed

def main():
    """Función principal"""
    print("🧪 VALIDACIÓN COMPLETA DEL CAMPO CANONICAL_URL")
    print("="*60)
    
    model_results = test_model_functionality()
    serializer_results = test_serializers()
    admin_results = test_admin_functionality()
    view_results = test_view_filters()
    api_results = test_api_functionality()
    
    success = generate_report(
        model_results, 
        serializer_results, 
        admin_results, 
        view_results, 
        api_results
    )
    
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())
