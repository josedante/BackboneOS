#!/usr/bin/env python3
"""
Script de pruebas de seguridad para BackboneOS
Valida que los endpoints estén correctamente protegidos
"""

import requests
import json
import sys
from urllib.parse import urljoin

# Configuración
BASE_URL = "http://localhost:8000"
API_BASE = f"{BASE_URL}/api/"

class SecurityTester:
    def __init__(self):
        self.session = requests.Session()
        self.token = None
        self.results = {
            'passed': 0,
            'failed': 0,
            'errors': []
        }

    def log(self, message, status="INFO"):
        print(f"[{status}] {message}")

    def test_endpoint(self, endpoint, method="GET", should_be_protected=True, data=None):
        """Prueba un endpoint específico"""
        url = urljoin(API_BASE, endpoint)
        
        try:
            # Prueba sin autenticación
            if method == "GET":
                response = self.session.get(url)
            elif method == "POST":
                response = self.session.post(url, json=data or {})
            elif method == "PUT":
                response = self.session.put(url, json=data or {})
            elif method == "DELETE":
                response = self.session.delete(url)
            else:
                response = self.session.get(url)

            if should_be_protected:
                if response.status_code in [401, 403]:
                    self.log(f"✅ {method} {endpoint} - Correctamente protegido ({response.status_code})", "PASS")
                    self.results['passed'] += 1
                    return True
                else:
                    self.log(f"❌ {method} {endpoint} - NO protegido (status: {response.status_code})", "FAIL")
                    self.results['failed'] += 1
                    self.results['errors'].append(f"{method} {endpoint} - Acceso sin autenticación permitido")
                    return False
            else:
                if response.status_code in [200, 201]:
                    self.log(f"✅ {method} {endpoint} - Acceso público correcto ({response.status_code})", "PASS")
                    self.results['passed'] += 1
                    return True
                else:
                    self.log(f"⚠️  {method} {endpoint} - Acceso público fallido (status: {response.status_code})", "WARN")
                    return False

        except requests.exceptions.RequestException as e:
            self.log(f"❌ Error probando {endpoint}: {e}", "ERROR")
            self.results['errors'].append(f"Error de conexión en {endpoint}: {e}")
            return False

    def run_security_tests(self):
        """Ejecuta todas las pruebas de seguridad"""
        self.log("🔒 Iniciando pruebas de seguridad de BackboneOS", "INFO")
        self.log("=" * 60, "INFO")

        # Verificar que el servidor esté funcionando
        try:
            response = requests.get(BASE_URL, timeout=5)
            self.log(f"✅ Servidor disponible en {BASE_URL}", "INFO")
        except requests.exceptions.RequestException:
            self.log(f"❌ Servidor no disponible en {BASE_URL}", "ERROR")
            return False

        # Pruebas de endpoints protegidos - Products
        self.log("\n📦 Probando endpoints de Products", "INFO")
        
        # ViewSets de productos - Deberían estar protegidos para escritura
        self.test_endpoint("products/products/", "GET", should_be_protected=False)  # Lectura pública
        self.test_endpoint("products/products/", "POST", should_be_protected=True)  # Escritura protegida
        self.test_endpoint("products/products/1/", "PUT", should_be_protected=True)
        self.test_endpoint("products/products/1/", "DELETE", should_be_protected=True)

        # Categorías - Lectura pública, escritura protegida
        self.test_endpoint("products/categories/", "GET", should_be_protected=False)
        self.test_endpoint("products/categories/", "POST", should_be_protected=True)

        # Modalidades - Lectura pública, escritura protegida
        self.test_endpoint("products/modalities/", "GET", should_be_protected=False)
        self.test_endpoint("products/modalities/", "POST", should_be_protected=True)

        # Customizaciones - Lectura pública, escritura protegida
        self.test_endpoint("products/customizations/", "GET", should_be_protected=False)
        self.test_endpoint("products/customizations/", "POST", should_be_protected=True)

        # Analytics - Completamente protegidos
        self.log("\n📊 Probando endpoints de Analytics", "INFO")
        
        analytics_endpoints = [
            "products/analytics/division-dashboard/",
            "products/analytics/product-dashboard/",
            "products/analytics/category-analytics/",
            "products/analytics/market-segmentation/",
            "products/analytics/pricing-analytics/",
            "products/analytics/growth-analytics/",
            "products/analytics/recommendations/"
        ]
        
        for endpoint in analytics_endpoints:
            self.test_endpoint(endpoint, "GET", should_be_protected=True)

        # Pruebas de endpoints de World (ya estaban protegidos)
        self.log("\n🌍 Probando endpoints de World", "INFO")
        
        world_endpoints = [
            "world/countries/",
            "world/states/",
            "world/cities/",
            "world/divisions/"
        ]
        
        for endpoint in world_endpoints:
            self.test_endpoint(endpoint, "GET", should_be_protected=False)  # Lectura pública
            self.test_endpoint(endpoint, "POST", should_be_protected=True)  # Escritura protegida

        # Resumen de resultados
        self.log("\n" + "=" * 60, "INFO")
        self.log("📋 RESUMEN DE RESULTADOS DE SEGURIDAD", "INFO")
        self.log("=" * 60, "INFO")
        
        total_tests = self.results['passed'] + self.results['failed']
        self.log(f"Total de pruebas: {total_tests}", "INFO")
        self.log(f"✅ Pasaron: {self.results['passed']}", "PASS")
        self.log(f"❌ Fallaron: {self.results['failed']}", "FAIL")
        
        if self.results['failed'] > 0:
            self.log(f"\n⚠️  VULNERABILIDADES ENCONTRADAS:", "WARN")
            for error in self.results['errors']:
                self.log(f"  • {error}", "ERROR")
            return False
        else:
            self.log(f"\n🎉 ¡Todas las pruebas de seguridad pasaron exitosamente!", "PASS")
            return True

def main():
    """Función principal"""
    tester = SecurityTester()
    success = tester.run_security_tests()
    
    if success:
        sys.exit(0)
    else:
        sys.exit(1)

if __name__ == "__main__":
    main()
