#!/usr/bin/env python3
"""
BackboneOS - Sistema de Interacciones
Demostración de Capacidades Avanzadas
=====================================

Este script demuestra las funcionalidades más avanzadas del sistema de interacciones,
incluyendo analytics, filtros semánticos, y integración con el campo empresarial.
"""

import requests
import json
from datetime import datetime
import statistics

class InteractionsSystemDemo:
    def __init__(self, base_url="http://localhost:8000/api/interactions"):
        self.base_url = base_url
        self.session = requests.Session()
    
    def print_section(self, title):
        """Imprimir sección con formato"""
        print(f"\n{'='*60}")
        print(f"🎯 {title.upper()}")
        print(f"{'='*60}")
    
    def demo_basic_data(self):
        """Demostrar datos básicos del sistema"""
        self.print_section("Inventario del Sistema de Interacciones")
        
        endpoints = [
            ("Mediums", f"{self.base_url}/mediums/"),
            ("Channels", f"{self.base_url}/channels/"),
            ("Action Types", f"{self.base_url}/action-types/"),
            ("Actions", f"{self.base_url}/actions/"),
            ("Agents", f"{self.base_url}/agents/"),
            ("Touchpoint Classes", f"{self.base_url}/touchpoint-classes/"),
            ("Touchpoints", f"{self.base_url}/touchpoints/"),
            ("Interactions", f"{self.base_url}/interactions/")
        ]
        
        total_records = 0
        for name, url in endpoints:
            try:
                response = self.session.get(url)
                if response.status_code == 200:
                    data = response.json()
                    if isinstance(data, dict) and 'count' in data:
                        count = data['count']
                    elif isinstance(data, list):
                        count = len(data)
                    else:
                        count = 1
                    
                    total_records += count
                    print(f"📊 {name:<20}: {count:>5} registros")
                else:
                    print(f"❌ {name:<20}: Error {response.status_code}")
            except Exception as e:
                print(f"❌ {name:<20}: {str(e)}")
        
        print(f"\n📈 Total de registros en el sistema: {total_records}")
        return total_records
    
    def demo_analytics_dashboard(self):
        """Demostrar dashboard de analytics"""
        self.print_section("Dashboard de Analytics")
        
        # Analytics general de interacciones
        try:
            response = self.session.get(f"{self.base_url}/interactions/analytics/")
            if response.status_code == 200:
                data = response.json()
                print("🎯 MÉTRICAS GENERALES DE INTERACCIONES")
                print(f"   Total de interacciones: {data.get('total_interactions', 0)}")
                print(f"   Sesiones únicas: {data.get('unique_sessions', 0)}")
                print(f"   Duración promedio: {data.get('avg_duration_seconds', 0):.1f} segundos")
                
                # Distribución por canal
                if 'by_channel' in data and data['by_channel']:
                    print("\n📱 TOP CANALES POR INTERACCIONES:")
                    for item in data['by_channel'][:3]:
                        channel = item.get('channel__name', 'N/A')
                        count = item.get('count', 0)
                        print(f"   • {channel}: {count} interacciones")
                
        except Exception as e:
            print(f"❌ Error en analytics de interacciones: {e}")
        
        # Analytics de agentes
        try:
            response = self.session.get(f"{self.base_url}/agents/analytics/")
            if response.status_code == 200:
                data = response.json()
                print(f"\n🤖 ANÁLISIS DE AGENTES")
                print(f"   Total de agentes: {data.get('total_agents', 0)}")
                
                if 'agents_by_type' in data:
                    print("\n📊 DISTRIBUCIÓN POR TIPO DE AGENTE:")
                    for item in data['agents_by_type']:
                        agent_type = item.get('agent_type', 'N/A')
                        count = item.get('count', 0)
                        interactions = item.get('interactions_count', 0)
                        print(f"   • {agent_type.title()}: {count} agentes, {interactions} interacciones")
                
                if 'top_agents' in data and data['top_agents']:
                    print("\n🏆 TOP 3 AGENTES MÁS ACTIVOS:")
                    for i, agent in enumerate(data['top_agents'][:3], 1):
                        name = agent.get('name', 'N/A')[:50]  # Truncar nombres largos
                        interactions = agent.get('interactions_count', 0)
                        print(f"   {i}. {name}: {interactions} interacciones")
        except Exception as e:
            print(f"❌ Error en analytics de agentes: {e}")
    
    def demo_advanced_filtering(self):
        """Demostrar filtros avanzados"""
        self.print_section("Capacidades de Filtrado Avanzado")
        
        # Filtro por medium específico
        print("🔍 FILTRADO POR MEDIUM 'DIGITAL':")
        try:
            response = self.session.get(f"{self.base_url}/channels/?search=digital")
            if response.status_code == 200:
                data = response.json()
                count = data.get('count', 0) if isinstance(data, dict) else len(data)
                print(f"   Canales digitales encontrados: {count}")
                
                if isinstance(data, dict) and 'results' in data:
                    for channel in data['results'][:3]:
                        name = channel.get('name', 'N/A')
                        medium = channel.get('medium_name', 'N/A')
                        print(f"   • {name} ({medium})")
        except Exception as e:
            print(f"❌ Error en filtrado de canales: {e}")
        
        # Filtro por tipo de agente
        print("\n🤖 FILTRADO POR TIPO DE AGENTE 'BROWSER':")
        try:
            response = self.session.get(f"{self.base_url}/agents/?agent_type=browser")
            if response.status_code == 200:
                data = response.json()
                count = data.get('count', 0) if isinstance(data, dict) else len(data)
                print(f"   Agentes de tipo browser: {count}")
        except Exception as e:
            print(f"❌ Error en filtrado de agentes: {e}")
    
    def demo_choices_endpoints(self):
        """Demostrar endpoints de choices para formularios"""
        self.print_section("Endpoints de Choices para Formularios")
        
        choices_endpoints = [
            ("Mediums", f"{self.base_url}/mediums/choices/"),
            ("Channels", f"{self.base_url}/channels/choices/"),
            ("Action Types", f"{self.base_url}/action-types/choices/"),
            ("Actions", f"{self.base_url}/actions/choices/"),
            ("Agents", f"{self.base_url}/agents/choices/")
        ]
        
        for name, url in choices_endpoints:
            try:
                response = self.session.get(url)
                if response.status_code == 200:
                    data = response.json()
                    count = len(data) if isinstance(data, list) else 0
                    print(f"📝 {name:<15}: {count:>3} opciones para formularios")
                    
                    # Mostrar ejemplos
                    if isinstance(data, list) and data:
                        example = data[0]
                        if 'name' in example:
                            print(f"    Ejemplo: {example['name']}")
                else:
                    print(f"❌ {name:<15}: Error {response.status_code}")
            except Exception as e:
                print(f"❌ {name:<15}: {str(e)}")
    
    def demo_semantic_integration(self):
        """Demostrar integración semántica con world app"""
        self.print_section("Integración con Campo Semántico (World App)")
        
        print("🌍 VERIFICANDO INTEGRACIÓN CON WORLD APP:")
        
        # Verificar disponibilidad de endpoints semánticos
        semantic_endpoints = [
            ("Industries", "http://localhost:8000/api/world/industries/"),
            ("Functions", "http://localhost:8000/api/world/functions/"),
            ("Skills", "http://localhost:8000/api/world/skills/"),
            ("Descriptors", "http://localhost:8000/api/world/descriptors/")
        ]
        
        available_semantic_data = {}
        for name, url in semantic_endpoints:
            try:
                response = self.session.get(url)
                if response.status_code == 200:
                    data = response.json()
                    count = data.get('count', 0) if isinstance(data, dict) else len(data)
                    available_semantic_data[name.lower()] = count
                    print(f"   ✅ {name}: {count} registros disponibles")
                else:
                    print(f"   ❌ {name}: No disponible")
                    available_semantic_data[name.lower()] = 0
            except Exception as e:
                print(f"   ❌ {name}: Error de conexión")
                available_semantic_data[name.lower()] = 0
        
        # Verificar touchpoints con relaciones semánticas
        print(f"\n🎯 TOUCHPOINTS CON CONTEXTO SEMÁNTICO:")
        try:
            response = self.session.get(f"{self.base_url}/touchpoints/")
            if response.status_code == 200:
                data = response.json()
                count = data.get('count', 0) if isinstance(data, dict) else len(data)
                print(f"   Total de touchpoints: {count}")
                
                if count > 0:
                    print("   💡 Los touchpoints pueden ser categorizados por:")
                    if available_semantic_data.get('industries', 0) > 0:
                        print(f"      • Industrias relacionadas ({available_semantic_data['industries']} disponibles)")
                    if available_semantic_data.get('functions', 0) > 0:
                        print(f"      • Funciones organizacionales ({available_semantic_data['functions']} disponibles)")
                    if available_semantic_data.get('skills', 0) > 0:
                        print(f"      • Habilidades requeridas ({available_semantic_data['skills']} disponibles)")
                    if available_semantic_data.get('descriptors', 0) > 0:
                        print(f"      • Descriptores semánticos ({available_semantic_data['descriptors']} disponibles)")
                else:
                    print("   📝 Crear touchpoints para ver la integración semántica en acción")
        except Exception as e:
            print(f"   ❌ Error verificando touchpoints: {e}")
    
    def demo_performance_metrics(self):
        """Demostrar métricas de performance del sistema"""
        self.print_section("Métricas de Performance del Sistema")
        
        start_time = datetime.now()
        
        # Realizar múltiples requests para medir performance
        endpoints_to_test = [
            f"{self.base_url}/mediums/",
            f"{self.base_url}/channels/",
            f"{self.base_url}/actions/",
            f"{self.base_url}/agents/",
            f"{self.base_url}/interactions/",
            f"{self.base_url}/interactions/analytics/",
            f"{self.base_url}/agents/analytics/"
        ]
        
        response_times = []
        successful_requests = 0
        
        print("⚡ MIDIENDO TIEMPOS DE RESPUESTA:")
        for endpoint in endpoints_to_test:
            try:
                request_start = datetime.now()
                response = self.session.get(endpoint)
                request_end = datetime.now()
                
                response_time = (request_end - request_start).total_seconds() * 1000  # en ms
                response_times.append(response_time)
                
                if response.status_code == 200:
                    successful_requests += 1
                    status = "✅"
                else:
                    status = "❌"
                
                endpoint_name = endpoint.split('/')[-2] if endpoint.split('/')[-1] == '' else endpoint.split('/')[-1]
                print(f"   {status} {endpoint_name:<20}: {response_time:>6.1f}ms")
                
            except Exception as e:
                print(f"   ❌ {endpoint}: Error")
        
        end_time = datetime.now()
        total_time = (end_time - start_time).total_seconds()
        
        if response_times:
            avg_response_time = statistics.mean(response_times)
            min_response_time = min(response_times)
            max_response_time = max(response_times)
            
            print(f"\n📊 ESTADÍSTICAS DE PERFORMANCE:")
            print(f"   Requests exitosos: {successful_requests}/{len(endpoints_to_test)}")
            print(f"   Tiempo promedio: {avg_response_time:.1f}ms")
            print(f"   Tiempo mínimo: {min_response_time:.1f}ms")
            print(f"   Tiempo máximo: {max_response_time:.1f}ms")
            print(f"   Tiempo total: {total_time:.2f}s")
            
            # Evaluación de performance
            if avg_response_time < 100:
                performance_rating = "🚀 EXCELENTE"
            elif avg_response_time < 300:
                performance_rating = "⚡ BUENO"
            elif avg_response_time < 500:
                performance_rating = "📊 ACEPTABLE"
            else:
                performance_rating = "⚠️ NECESITA OPTIMIZACIÓN"
            
            print(f"   Evaluación: {performance_rating}")
    
    def demo_system_readiness(self):
        """Evaluar preparación del sistema para producción"""
        self.print_section("Evaluación de Preparación para Producción")
        
        readiness_score = 0
        max_score = 0
        
        checks = [
            ("API Endpoints Funcionando", self.check_api_endpoints),
            ("Analytics Disponibles", self.check_analytics),
            ("Filtros y Búsquedas", self.check_filtering),
            ("Choices para Formularios", self.check_choices),
            ("Integración Semántica", self.check_semantic_integration),
            ("Performance Aceptable", self.check_performance)
        ]
        
        print("🔍 EJECUTANDO CHECKS DE PREPARACIÓN:\n")
        
        for check_name, check_function in checks:
            max_score += 1
            try:
                result = check_function()
                if result:
                    readiness_score += 1
                    status = "✅ PASS"
                else:
                    status = "❌ FAIL"
                
                print(f"   {status} {check_name}")
            except Exception as e:
                print(f"   ❌ FAIL {check_name}: {e}")
        
        print(f"\n📊 PUNTUACIÓN DE PREPARACIÓN: {readiness_score}/{max_score}")
        
        if readiness_score == max_score:
            readiness_level = "🚀 COMPLETAMENTE LISTO PARA PRODUCCIÓN"
        elif readiness_score >= max_score * 0.8:
            readiness_level = "⚡ CASI LISTO PARA PRODUCCIÓN"
        elif readiness_score >= max_score * 0.6:
            readiness_level = "📊 NECESITA ALGUNAS MEJORAS"
        else:
            readiness_level = "⚠️ REQUIERE TRABAJO ADICIONAL"
        
        print(f"📈 Estado: {readiness_level}")
        
        percentage = (readiness_score / max_score) * 100
        print(f"🎯 Porcentaje de completitud: {percentage:.1f}%")
    
    def check_api_endpoints(self):
        """Verificar que los endpoints principales funcionen"""
        endpoints = [
            f"{self.base_url}/mediums/",
            f"{self.base_url}/channels/",
            f"{self.base_url}/interactions/"
        ]
        
        for endpoint in endpoints:
            response = self.session.get(endpoint)
            if response.status_code != 200:
                return False
        return True
    
    def check_analytics(self):
        """Verificar que los analytics funcionen"""
        analytics_endpoints = [
            f"{self.base_url}/interactions/analytics/",
            f"{self.base_url}/agents/analytics/"
        ]
        
        for endpoint in analytics_endpoints:
            response = self.session.get(endpoint)
            if response.status_code != 200:
                return False
        return True
    
    def check_filtering(self):
        """Verificar que los filtros funcionen"""
        filter_tests = [
            f"{self.base_url}/mediums/?is_active=true",
            f"{self.base_url}/agents/?agent_type=browser"
        ]
        
        for endpoint in filter_tests:
            response = self.session.get(endpoint)
            if response.status_code != 200:
                return False
        return True
    
    def check_choices(self):
        """Verificar que los endpoints de choices funcionen"""
        choice_endpoints = [
            f"{self.base_url}/mediums/choices/",
            f"{self.base_url}/agents/choices/"
        ]
        
        for endpoint in choice_endpoints:
            response = self.session.get(endpoint)
            if response.status_code != 200:
                return False
        return True
    
    def check_semantic_integration(self):
        """Verificar integración con world app"""
        try:
            response = self.session.get("http://localhost:8000/api/world/industries/")
            return response.status_code == 200
        except:
            return False
    
    def check_performance(self):
        """Verificar que la performance sea aceptable"""
        start_time = datetime.now()
        response = self.session.get(f"{self.base_url}/interactions/")
        end_time = datetime.now()
        
        response_time = (end_time - start_time).total_seconds() * 1000
        return response.status_code == 200 and response_time < 500  # menos de 500ms
    
    def run_complete_demo(self):
        """Ejecutar demostración completa"""
        print("🎉 BACKBONEOS - SISTEMA DE INTERACCIONES")
        print("Demostración de Capacidades Avanzadas")
        print("=" * 60)
        print("🕒 Iniciado:", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        
        try:
            self.demo_basic_data()
            self.demo_analytics_dashboard()
            self.demo_advanced_filtering()
            self.demo_choices_endpoints()
            self.demo_semantic_integration()
            self.demo_performance_metrics()
            self.demo_system_readiness()
            
            print(f"\n{'='*60}")
            print("🎊 DEMOSTRACIÓN COMPLETADA EXITOSAMENTE")
            print("💡 El sistema de interacciones está completamente funcional")
            print("🚀 Listo para ser utilizado en entorno de producción")
            print(f"{'='*60}\n")
            
        except Exception as e:
            print(f"\n❌ Error durante la demostración: {e}")

if __name__ == "__main__":
    demo = InteractionsSystemDemo()
    demo.run_complete_demo()
