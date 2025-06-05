#!/usr/bin/env python3
"""
Script de prueba para verificar la seguridad de los endpoints de BackboneOS
Ejecutar desde el directorio raíz del proyecto: python test_security.py
"""

import requests
import json
import sys

# Configuración
BASE_URL = "http://localhost:8000"
TEST_USER = {
    "username": "testuser", 
    "password": "testpass123"
}

class SecurityTester:
    def __init__(self):
        self.base_url = BASE_URL
        self.session = requests.Session()
        self.token = None
        
    def test_endpoint(self, method, endpoint, authenticated=False, description=""):
        """Prueba un endpoint específico"""
        url = f"{self.base_url}{endpoint}"
        headers = {}
        
        if authenticated and self.token:
            headers['Authorization'] = f'Bearer {self.token}'
            
        try:
            response = self.session.request(method, url, headers=headers)
            return {
                'endpoint': endpoint,
                'method': method,
                'status': response.status_code,
                'authenticated': authenticated,
                'success': response.status_code < 400,
                'description': description
            }
        except Exception as e:
            return {
                'endpoint': endpoint,
                'method': method,
                'status': 'ERROR',
                'authenticated': authenticated,
                'success': False,
                'description': f"{description} - Error: {str(e)}"
            }
    
    def login(self):
        """Intenta hacer login para obtener token"""
        try:
            response = self.session.post(
                f"{self.base_url}/api/auth/jwt/login/",
                json=TEST_USER
            )
            if response.status_code == 200:
                data = response.json()
                self.token = data.get('access')
                return True
            return False
        except:
            return False
    
    def run_security_tests(self):
        """Ejecuta todas las pruebas de seguridad"""
        print("🔒 INICIO DE PRUEBAS DE SEGURIDAD - BackboneOS")
        print("=" * 60)
        
        # Pruebas sin autenticación
        print("\n📂 PRUEBAS SIN AUTENTICACIÓN (deben permitir solo lectura)")
        unauthenticated_tests = [
            ("GET", "/api/world/countries/", "Países - lectura pública"),
            ("GET", "/api/products/categories/", "Categorías - lectura pública"),
            ("GET", "/api/products/modalities/", "Modalidades - lectura pública"),
            ("GET", "/api/products/products/", "Productos - lectura pública"),
            ("POST", "/api/products/products/", "Productos - escritura protegida"),
            ("GET", "/api/products/analytics/dashboard/", "Analytics - completamente protegido"),
        ]
        
        for method, endpoint, desc in unauthenticated_tests:
            result = self.test_endpoint(method, endpoint, False, desc)
            self.print_result(result)
        
        # Intentar login
        print("\n🔑 PRUEBA DE AUTENTICACIÓN")
        if self.login():
            print("✅ Login exitoso - Token obtenido")
        else:
            print("❌ Login falló - Creando usuario de prueba...")
            # Aquí podrías agregar lógica para crear usuario de prueba
        
        # Pruebas con autenticación
        if self.token:
            print("\n🔐 PRUEBAS CON AUTENTICACIÓN (deben permitir todas las operaciones)")
            authenticated_tests = [
                ("GET", "/api/products/analytics/dashboard/", "Analytics - con auth"),
                ("GET", "/api/products/products/stats/", "Estadísticas - con auth"),
                ("POST", "/api/products/categories/", "Crear categoría - con auth"),
                ("GET", "/api/products/analytics/pricing/", "Pricing analytics - con auth"),
            ]
            
            for method, endpoint, desc in authenticated_tests:
                result = self.test_endpoint(method, endpoint, True, desc)
                self.print_result(result)
        
        print("\n" + "=" * 60)
        print("🔒 PRUEBAS DE SEGURIDAD COMPLETADAS")
    
    def print_result(self, result):
        """Imprime el resultado de una prueba"""
        status_icon = "✅" if result['success'] else "❌"
        auth_text = "🔐" if result['authenticated'] else "🌐"
        
        print(f"{status_icon} {auth_text} {result['method']} {result['endpoint']}")
        print(f"   Status: {result['status']} - {result['description']}")
        
        # Análisis de seguridad
        if not result['authenticated'] and result['method'] == 'GET' and result['success']:
            print("   ℹ️  Acceso público de lectura - OK")
        elif not result['authenticated'] and result['method'] != 'GET' and not result['success']:
            print("   🛡️  Escritura protegida correctamente")
        elif not result['authenticated'] and 'analytics' in result['endpoint'] and not result['success']:
            print("   🔒 Analytics protegido correctamente")
        elif result['authenticated'] and result['success']:
            print("   ✅ Acceso autenticado funcionando")
        
        print()

if __name__ == "__main__":
    print("🔍 Verificando que el servidor esté ejecutándose...")
    try:
        response = requests.get(f"{BASE_URL}/api/", timeout=5)
        print("✅ Servidor disponible")
    except:
        print("❌ Error: El servidor no está disponible en http://localhost:8000")
        print("   Asegúrate de que docker-compose esté ejecutándose:")
        print("   docker-compose up -d")
        sys.exit(1)
    
    tester = SecurityTester()
    tester.run_security_tests()
