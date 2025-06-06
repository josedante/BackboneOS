#!/usr/bin/env python3
"""
Script de pruebas completas para la API del sistema de interacciones BackboneOS.
Verifica todos los endpoints, funcionalidades y analytics.
"""

import requests
import json
import sys
from datetime import datetime


class InteractionsAPITester:
    def __init__(self, base_url="http://localhost:8000"):
        self.base_url = base_url
        self.api_url = f"{base_url}/api/interactions"
        self.results = {
            'total_tests': 0,
            'passed': 0,
            'failed': 0,
            'errors': []
        }
    
    def log(self, message, level="INFO"):
        """Log con timestamp"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"[{timestamp}] {level}: {message}")
    
    def test_endpoint(self, endpoint, description, expected_keys=None, expected_count=None):
        """Prueba un endpoint específico"""
        self.results['total_tests'] += 1
        
        try:
            self.log(f"Probando {endpoint} - {description}")
            response = requests.get(f"{self.api_url}{endpoint}")
            
            if response.status_code != 200:
                error_msg = f"❌ {endpoint}: HTTP {response.status_code} - {response.text[:100]}"
                self.log(error_msg, "ERROR")
                self.results['errors'].append(error_msg)
                self.results['failed'] += 1
                return False
            
            data = response.json()
            
            # Verificar claves esperadas
            if expected_keys:
                for key in expected_keys:
                    if key not in data:
                        error_msg = f"❌ {endpoint}: Falta clave '{key}' en respuesta"
                        self.log(error_msg, "ERROR")
                        self.results['errors'].append(error_msg)
                        self.results['failed'] += 1
                        return False
            
            # Verificar conteo esperado
            if expected_count is not None:
                actual_count = data.get('count', len(data) if isinstance(data, list) else 0)
                if actual_count != expected_count:
                    error_msg = f"❌ {endpoint}: Esperaba {expected_count} registros, obtuvo {actual_count}"
                    self.log(error_msg, "ERROR")
                    self.results['errors'].append(error_msg)
                    self.results['failed'] += 1
                    return False
            
            self.log(f"✅ {endpoint}: OK", "SUCCESS")
            self.results['passed'] += 1
            return True
            
        except Exception as e:
            error_msg = f"❌ {endpoint}: Excepción - {str(e)}"
            self.log(error_msg, "ERROR")
            self.results['errors'].append(error_msg)
            self.results['failed'] += 1
            return False
    
    def run_basic_endpoints_tests(self):
        """Prueba todos los endpoints básicos"""
        self.log("=== PRUEBAS DE ENDPOINTS BÁSICOS ===")
        
        # Endpoints principales
        endpoints = [
            ("/mediums/", "Mediums - Lista", ["count", "results"], 4),
            ("/channels/", "Channels - Lista", ["count", "results"], 8),
            ("/action-types/", "Action Types - Lista", ["count", "results"], 4),
            ("/actions/", "Actions - Lista", ["count", "results"], 8),
            ("/agents/", "Agents - Lista", ["count", "results"]),
            ("/touchpoint-classes/", "Touchpoint Classes - Lista", ["count", "results"]),
            ("/touchpoints/", "Touchpoints - Lista", ["count", "results"]),
            ("/interactions/", "Interactions - Lista", ["count", "results"]),
        ]
        
        for endpoint, description, expected_keys, *expected_count in endpoints:
            count = expected_count[0] if expected_count else None
            self.test_endpoint(endpoint, description, expected_keys, count)
    
    def run_choices_endpoints_tests(self):
        """Prueba endpoints de choices"""
        self.log("=== PRUEBAS DE ENDPOINTS CHOICES ===")
        
        choices_endpoints = [
            ("/mediums/choices/", "Mediums - Choices"),
            ("/channels/choices/", "Channels - Choices"),
            ("/action-types/choices/", "Action Types - Choices"),
            ("/actions/choices/", "Actions - Choices"),
            ("/agents/choices/", "Agents - Choices"),
            ("/touchpoint-classes/choices/", "Touchpoint Classes - Choices"),
            ("/touchpoints/choices/", "Touchpoints - Choices"),
        ]
        
        for endpoint, description in choices_endpoints:
            self.test_endpoint(endpoint, description)
    
    def run_filter_tests(self):
        """Prueba filtros en endpoints"""
        self.log("=== PRUEBAS DE FILTROS ===")
        
        filter_tests = [
            ("/mediums/?is_active=true", "Mediums - Filtro activos"),
            ("/channels/?medium=f47ac10b-58cc-4372-a567-0e02b2c3d479", "Channels - Filtro por medium"),
            ("/actions/?action_type=975877cb-e92a-4671-a07d-25af42ae2fc0", "Actions - Filtro por action_type"),
            ("/interactions/?jtbd_stage=any", "Interactions - Filtro por JTBD stage"),
        ]
        
        for endpoint, description in filter_tests:
            self.test_endpoint(endpoint, description, ["count", "results"])
    
    def run_search_tests(self):
        """Prueba búsquedas en endpoints"""
        self.log("=== PRUEBAS DE BÚSQUEDA ===")
        
        search_tests = [
            ("/mediums/?search=digital", "Mediums - Búsqueda 'digital'"),
            ("/channels/?search=web", "Channels - Búsqueda 'web'"),
            ("/actions/?search=click", "Actions - Búsqueda 'click'"),
        ]
        
        for endpoint, description in search_tests:
            self.test_endpoint(endpoint, description, ["count", "results"])
    
    def run_analytics_tests(self):
        """Prueba endpoints de analytics"""
        self.log("=== PRUEBAS DE ANALYTICS ===")
        
        analytics_endpoints = [
            ("/interactions/analytics/", "Analytics - Dashboard general"),
            ("/agents/analytics/", "Analytics - Agents"),
            ("/touchpoints/analytics/", "Analytics - Touchpoints"),
        ]
        
        for endpoint, description in analytics_endpoints:
            self.test_endpoint(endpoint, description)
    
    def run_individual_record_tests(self):
        """Prueba acceso a registros individuales"""
        self.log("=== PRUEBAS DE REGISTROS INDIVIDUALES ===")
        
        try:
            # Obtener IDs de registros existentes
            mediums_response = requests.get(f"{self.api_url}/mediums/")
            if mediums_response.status_code == 200:
                mediums_data = mediums_response.json()
                if mediums_data.get('results'):
                    medium_id = mediums_data['results'][0]['id']
                    self.test_endpoint(f"/mediums/{medium_id}/", "Medium - Detalle individual")
            
            channels_response = requests.get(f"{self.api_url}/channels/")
            if channels_response.status_code == 200:
                channels_data = channels_response.json()
                if channels_data.get('results'):
                    channel_id = channels_data['results'][0]['id']
                    self.test_endpoint(f"/channels/{channel_id}/", "Channel - Detalle individual")
        
        except Exception as e:
            self.log(f"Error en pruebas individuales: {e}", "ERROR")
    
    def run_all_tests(self):
        """Ejecuta todas las pruebas"""
        self.log("🚀 INICIANDO PRUEBAS COMPLETAS DE LA API DE INTERACTIONS")
        self.log("=" * 60)
        
        start_time = datetime.now()
        
        # Ejecutar grupos de pruebas
        self.run_basic_endpoints_tests()
        self.run_choices_endpoints_tests()
        self.run_filter_tests()
        self.run_search_tests()
        self.run_analytics_tests()
        self.run_individual_record_tests()
        
        # Resumen final
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        self.log("=" * 60)
        self.log("📊 RESUMEN DE PRUEBAS")
        self.log(f"Total de pruebas: {self.results['total_tests']}")
        self.log(f"✅ Exitosas: {self.results['passed']}")
        self.log(f"❌ Fallidas: {self.results['failed']}")
        self.log(f"⏱️ Duración: {duration:.2f} segundos")
        
        if self.results['errors']:
            self.log("\n🔥 ERRORES ENCONTRADOS:")
            for error in self.results['errors']:
                self.log(f"  • {error}")
        
        success_rate = (self.results['passed'] / self.results['total_tests']) * 100
        self.log(f"\n📈 Tasa de éxito: {success_rate:.1f}%")
        
        if success_rate >= 90:
            self.log("🎉 ¡EXCELENTE! La API está funcionando correctamente", "SUCCESS")
            return True
        elif success_rate >= 70:
            self.log("⚠️ BUENO: La API funciona con algunos problemas menores", "WARNING")
            return True
        else:
            self.log("💥 CRÍTICO: La API tiene problemas significativos", "ERROR")
            return False


def main():
    """Función principal"""
    print("BackboneOS - Sistema de Interacciones")
    print("Pruebas Completas de API")
    print("=" * 50)
    
    # Crear instancia del tester
    tester = InteractionsAPITester()
    
    # Ejecutar todas las pruebas
    success = tester.run_all_tests()
    
    # Código de salida
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
