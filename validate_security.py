#!/usr/bin/env python3
"""
Script de validación de seguridad para BackboneOS
Valida que los endpoints estén correctamente protegidos después de las correcciones
"""

import requests
import json
import sys

BASE_URL = "http://localhost:8000"
API_BASE = f"{BASE_URL}/api/"

def test_endpoint(endpoint, method="GET", should_be_protected=True, description=""):
    """Prueba un endpoint específico"""
    url = f"{API_BASE}{endpoint}"
    
    try:
        if method == "GET":
            response = requests.get(url, timeout=10)
        elif method == "POST":
            response = requests.post(url, json={"test": "data"}, timeout=10)
        else:
            response = requests.get(url, timeout=10)

        if should_be_protected:
            if response.status_code in [401, 403]:
                print(f"✅ {method} {endpoint} - Protegido correctamente ({response.status_code}) - {description}")
                return True
            else:
                print(f"❌ {method} {endpoint} - NO protegido (status: {response.status_code}) - {description}")
                return False
        else:
            if response.status_code == 200:
                print(f"✅ {method} {endpoint} - Acceso público correcto - {description}")
                return True
            else:
                print(f"⚠️  {method} {endpoint} - Acceso público con estado {response.status_code} - {description}")
                return False

    except requests.exceptions.RequestException as e:
        print(f"❌ Error probando {endpoint}: {e}")
        return False

def main():
    print("🔒 VALIDACIÓN DE SEGURIDAD DE BACKBONEOS")
    print("=" * 60)
    
    # Verificar servidor
    try:
        response = requests.get(BASE_URL, timeout=5)
        print(f"✅ Servidor disponible en {BASE_URL}")
    except:
        print(f"❌ Servidor no disponible en {BASE_URL}")
        return False

    print("\n📊 PROBANDO ENDPOINTS DE ANALYTICS (DEBEN ESTAR PROTEGIDOS)")
    print("-" * 50)
    
    analytics_tests = [
        ("products/analytics/dashboard/", "Analytics Dashboard"),
        ("products/analytics/divisions/", "Analytics Divisiones"),
        ("products/analytics/categories/", "Analytics Categorías"),
        ("products/analytics/market-segmentation/", "Analytics Segmentación"),
        ("products/analytics/pricing/", "Analytics Precios"),
        ("products/analytics/growth/", "Analytics Crecimiento"),
        ("products/analytics/recommendations/", "Analytics Recomendaciones"),
    ]
    
    analytics_passed = 0
    for endpoint, desc in analytics_tests:
        if test_endpoint(endpoint, "GET", True, desc):
            analytics_passed += 1

    print(f"\n📦 PROBANDO ENDPOINTS DE PRODUCTS (LECTURA PÚBLICA, ESCRITURA PROTEGIDA)")
    print("-" * 50)
    
    products_tests = [
        # Lectura pública
        ("products/products/", "GET", False, "Productos - Lectura"),
        ("products/categories/", "GET", False, "Categorías - Lectura"),
        ("products/modalities/", "GET", False, "Modalidades - Lectura"),
        ("products/customizations/", "GET", False, "Customizaciones - Lectura"),
        
        # Escritura protegida
        ("products/products/", "POST", True, "Productos - Escritura"),
        ("products/categories/", "POST", True, "Categorías - Escritura"),
        ("products/modalities/", "POST", True, "Modalidades - Escritura"),
        ("products/customizations/", "POST", True, "Customizaciones - Escritura"),
    ]
    
    products_passed = 0
    for endpoint, method, should_be_protected, desc in products_tests:
        if test_endpoint(endpoint, method, should_be_protected, desc):
            products_passed += 1

    print(f"\n🌍 PROBANDO ENDPOINTS DE WORLD (LECTURA PÚBLICA, ESCRITURA PROTEGIDA)")
    print("-" * 50)
    
    world_tests = [
        # Lectura pública
        ("world/countries/", "GET", False, "Países - Lectura"),
        ("world/states/", "GET", False, "Estados - Lectura"),
        ("world/cities/", "GET", False, "Ciudades - Lectura"),
        ("world/divisions/", "GET", False, "Divisiones - Lectura"),
        
        # Escritura protegida
        ("world/countries/", "POST", True, "Países - Escritura"),
        ("world/states/", "POST", True, "Estados - Escritura"),
        ("world/cities/", "POST", True, "Ciudades - Escritura"),
        ("world/divisions/", "POST", True, "Divisiones - Escritura"),
    ]
    
    world_passed = 0
    for endpoint, method, should_be_protected, desc in world_tests:
        if test_endpoint(endpoint, method, should_be_protected, desc):
            world_passed += 1

    # Resumen
    total_analytics = len(analytics_tests)
    total_products = len(products_tests)
    total_world = len(world_tests)
    total_tests = total_analytics + total_products + total_world
    total_passed = analytics_passed + products_passed + world_passed

    print("\n" + "=" * 60)
    print("📋 RESUMEN DE RESULTADOS")
    print("=" * 60)
    print(f"Analytics: {analytics_passed}/{total_analytics} ✅")
    print(f"Products: {products_passed}/{total_products} ✅")
    print(f"World: {world_passed}/{total_world} ✅")
    print(f"TOTAL: {total_passed}/{total_tests} ✅")
    
    if total_passed == total_tests:
        print(f"\n🎉 ¡TODOS LOS TESTS PASARON! Sistema de seguridad funcionando correctamente.")
        return True
    else:
        print(f"\n⚠️  Algunos tests fallaron. Revisar configuración de seguridad.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
