#!/usr/bin/env python3
"""
Script de pruebas de performance para la aplicación entities.
Mide el rendimiento de consultas optimizadas vs no optimizadas.

Uso:
    python manage.py shell < entities/performance_tests.py
    
O desde shell de Django:
    exec(open('entities/performance_tests.py').read())
"""

import time
import statistics
from decimal import Decimal
from django.db import connection, transaction
from django.db.models import Count, Q, Prefetch, Avg, Max, Min
from django.utils import timezone

# Importar modelos
from entities.models import Person, Organization, ContactDetail, IndividualProfile, PhysicalAddress
from world.models import Country, Industry, Skill, AcademicDegree

class PerformanceTestRunner:
    """Ejecutor de pruebas de performance"""
    
    def __init__(self):
        self.results = []
        self.iterations = 5  # Número de iteraciones por prueba
        
    def time_query(self, query_func, description, iterations=None):
        """Ejecuta una consulta múltiples veces y mide el tiempo"""
        if iterations is None:
            iterations = self.iterations
            
        times = []
        query_count_before = len(connection.queries)
        
        for i in range(iterations):
            connection.queries_log.clear()
            start_time = time.time()
            
            # Ejecutar la consulta
            result = query_func()
            
            # Forzar evaluación si es QuerySet
            if hasattr(result, 'count') and not isinstance(result, list):
                count = result.count()
            elif hasattr(result, '__len__'):
                count = len(result)
            else:
                count = 1
                
            end_time = time.time()
            elapsed = end_time - start_time
            times.append(elapsed)
        
        query_count_after = len(connection.queries)
        avg_time = statistics.mean(times)
        min_time = min(times)
        max_time = max(times)
        std_dev = statistics.stdev(times) if len(times) > 1 else 0
        
        result = {
            'description': description,
            'avg_time': avg_time,
            'min_time': min_time,
            'max_time': max_time,
            'std_dev': std_dev,
            'iterations': iterations,
            'query_count': query_count_after - query_count_before,
            'record_count': count if 'count' in locals() else 'N/A'
        }
        
        self.results.append(result)
        return result
    
    def print_result(self, result):
        """Imprime resultado de una prueba"""
        print(f"📊 {result['description']}")
        print(f"   ⏱️  Tiempo promedio: {result['avg_time']*1000:.2f}ms")
        print(f"   📈 Rango: {result['min_time']*1000:.2f}ms - {result['max_time']*1000:.2f}ms")
        print(f"   📊 Desv. estándar: {result['std_dev']*1000:.2f}ms")
        print(f"   🔍 Consultas SQL: {result['query_count']}")
        print(f"   📝 Registros: {result['record_count']}")
        print()

def test_person_queries():
    """Pruebas de performance en modelo Person"""
    runner = PerformanceTestRunner()
    print("👥 PRUEBAS DE PERFORMANCE - PERSON")
    print("="*50)
    
    # 1. Búsqueda básica con índice
    result = runner.time_query(
        lambda: Person.objects.filter(is_active=True, gender='M').count(),
        "Filtrado por género activo (con índice)"
    )
    runner.print_result(result)
    
    # 2. Búsqueda demográfica compuesta
    result = runner.time_query(
        lambda: Person.objects.filter(
            is_active=True, 
            gender='F', 
            marital_status='SG'
        ).count(),
        "Filtrado demográfico compuesto"
    )
    runner.print_result(result)
    
    # 3. Búsqueda por país con relación
    result = runner.time_query(
        lambda: Person.objects.select_related('country_of_nationality').filter(
            is_active=True,
            country_of_nationality__name__icontains='Col'
        ).count(),
        "Filtrado por país con select_related"
    )
    runner.print_result(result)
    
    # 4. Búsqueda de contactos principales (optimizada)
    result = runner.time_query(
        lambda: Person.objects.prefetch_related(
            Prefetch('contacts', queryset=ContactDetail.objects.filter(is_primary=True))
        ).filter(is_active=True)[:50],
        "Carga de contactos principales con prefetch"
    )
    runner.print_result(result)
    
    # 5. Búsqueda de contactos principales (no optimizada)
    result = runner.time_query(
        lambda: [person.primary_contact for person in Person.objects.filter(is_active=True)[:50]],
        "Carga de contactos principales SIN prefetch"
    )
    runner.print_result(result)
    
    # 6. Búsqueda con perfil semántico (optimizada)
    result = runner.time_query(
        lambda: Person.objects.select_related('individualprofile__academic_degree').filter(
            is_active=True,
            individualprofile__isnull=False,
            individualprofile__allows_marketing=True
        )[:100],
        "Perfilado semántico optimizado"
    )
    runner.print_result(result)
    
    return runner.results

def test_organization_queries():
    """Pruebas de performance en modelo Organization"""
    runner = PerformanceTestRunner()
    print("🏢 PRUEBAS DE PERFORMANCE - ORGANIZATION")
    print("="*50)
    
    # 1. Filtrado por industria y país
    result = runner.time_query(
        lambda: Organization.objects.select_related('industry', 'country').filter(
            is_active=True,
            industry__isnull=False
        ).count(),
        "Filtrado por industria activa"
    )
    runner.print_result(result)
    
    # 2. Analytics organizacional
    result = runner.time_query(
        lambda: Organization.objects.values('org_type__name', 'country__name').annotate(
            count=Count('id')
        ).filter(is_active=True),
        "Analytics por tipo y país"
    )
    runner.print_result(result)
    
    # 3. Búsqueda de direcciones principales
    result = runner.time_query(
        lambda: Organization.objects.prefetch_related(
            Prefetch('physicaladdress_set', 
                    queryset=PhysicalAddress.objects.filter(is_primary=True))
        ).filter(is_active=True)[:50],
        "Carga de direcciones principales"
    )
    runner.print_result(result)
    
    return runner.results

def test_contact_queries():
    """Pruebas de performance en modelo ContactDetail"""
    runner = PerformanceTestRunner()
    print("📞 PRUEBAS DE PERFORMANCE - CONTACTDETAIL")
    print("="*50)
    
    # 1. Contactos verificados y principales
    result = runner.time_query(
        lambda: ContactDetail.objects.filter(
            is_active=True,
            is_primary=True,
            verified=True
        ).count(),
        "Contactos principales verificados"
    )
    runner.print_result(result)
    
    # 2. Búsqueda por email con verificación
    result = runner.time_query(
        lambda: ContactDetail.objects.filter(
            email__icontains='gmail',
            verified=True,
            is_active=True
        ).count(),
        "Búsqueda de emails verificados"
    )
    runner.print_result(result)
    
    # 3. Contactos por persona con relaciones
    result = runner.time_query(
        lambda: ContactDetail.objects.select_related('person').filter(
            person__is_active=True,
            is_active=True
        )[:100],
        "Contactos con select_related person"
    )
    runner.print_result(result)
    
    return runner.results

def test_profile_queries():
    """Pruebas de performance en modelo IndividualProfile"""
    runner = PerformanceTestRunner()
    print("👤 PRUEBAS DE PERFORMANCE - INDIVIDUALPROFILE")
    print("="*50)
    
    # 1. Perfiles con marketing habilitado
    result = runner.time_query(
        lambda: IndividualProfile.objects.filter(
            is_active=True,
            allows_marketing=True
        ).count(),
        "Perfiles con marketing habilitado"
    )
    runner.print_result(result)
    
    # 2. Perfiles por grado académico
    result = runner.time_query(
        lambda: IndividualProfile.objects.select_related('academic_degree').filter(
            is_active=True,
            academic_degree__isnull=False
        ).count(),
        "Perfiles con grado académico"
    )
    runner.print_result(result)
    
    # 3. Perfilado semántico completo (optimizado)
    result = runner.time_query(
        lambda: IndividualProfile.objects.select_related(
            'person', 'academic_degree'
        ).prefetch_related(
            'industries', 'skills', 'functions'
        ).filter(is_active=True)[:50],
        "Perfilado semántico completo optimizado"
    )
    runner.print_result(result)
    
    # 4. Perfilado semántico completo (no optimizado)
    result = runner.time_query(
        lambda: [
            {
                'person': profile.person.full_name,
                'industries': list(profile.industries.all()),
                'skills': list(profile.skills.all()),
                'functions': list(profile.functions.all())
            }
            for profile in IndividualProfile.objects.filter(is_active=True)[:50]
        ],
        "Perfilado semántico SIN optimización"
    )
    runner.print_result(result)
    
    return runner.results

def test_address_queries():
    """Pruebas de performance en modelo PhysicalAddress"""
    runner = PerformanceTestRunner()
    print("🏠 PRUEBAS DE PERFORMANCE - PHYSICALADDRESS")
    print("="*50)
    
    # 1. Direcciones principales por país
    result = runner.time_query(
        lambda: PhysicalAddress.objects.select_related('country').filter(
            is_active=True,
            is_primary=True
        ).count(),
        "Direcciones principales por país"
    )
    runner.print_result(result)
    
    # 2. Análisis geográfico
    result = runner.time_query(
        lambda: PhysicalAddress.objects.values('country__name', 'city').annotate(
            count=Count('id')
        ).filter(is_active=True),
        "Análisis geográfico por país-ciudad"
    )
    runner.print_result(result)
    
    # 3. Direcciones de facturación
    result = runner.time_query(
        lambda: PhysicalAddress.objects.filter(
            is_active=True,
            use_for_billing=True
        ).select_related('owner_org', 'owner_person').count(),
        "Direcciones de facturación"
    )
    runner.print_result(result)
    
    return runner.results

def test_complex_analytics():
    """Pruebas de consultas analíticas complejas"""
    runner = PerformanceTestRunner()
    print("📊 PRUEBAS DE PERFORMANCE - ANALYTICS COMPLEJOS")
    print("="*50)
    
    # 1. Dashboard de personas
    result = runner.time_query(
        lambda: {
            'total_personas': Person.objects.filter(is_active=True).count(),
            'por_genero': dict(Person.objects.filter(is_active=True).values('gender').annotate(count=Count('id')).values_list('gender', 'count')),
            'con_perfil': Person.objects.filter(is_active=True, individualprofile__isnull=False).count(),
            'marketing_habilitado': Person.objects.filter(is_active=True, individualprofile__allows_marketing=True).count()
        },
        "Dashboard de personas (múltiples consultas)"
    )
    runner.print_result(result)
    
    # 2. Dashboard organizacional
    result = runner.time_query(
        lambda: Organization.objects.filter(is_active=True).aggregate(
            total=Count('id'),
            por_industria=Count('id', filter=Q(industry__isnull=False)),
            con_direccion=Count('id', filter=Q(physicaladdress__is_primary=True))
        ),
        "Dashboard organizacional (agregaciones)"
    )
    runner.print_result(result)
    
    # 3. Análisis de contactabilidad
    result = runner.time_query(
        lambda: {
            'personas_contactables': Person.objects.filter(
                is_active=True,
                contacts__is_active=True,
                contacts__verified=True
            ).distinct().count(),
            'emails_verificados': ContactDetail.objects.filter(
                is_active=True,
                verified=True,
                email__isnull=False
            ).exclude(email='').count(),
            'telefonos_verificados': ContactDetail.objects.filter(
                is_active=True,
                verified=True,
                phone__isnull=False
            ).exclude(phone='').count()
        },
        "Análisis de contactabilidad"
    )
    runner.print_result(result)
    
    return runner.results

def generate_performance_report(all_results):
    """Genera reporte final de performance"""
    print("\n" + "="*70)
    print("📈 REPORTE FINAL DE PERFORMANCE")
    print("="*70)
    
    # Agrupar por categoría
    categories = {
        'Person': [],
        'Organization': [],
        'ContactDetail': [],
        'IndividualProfile': [],
        'PhysicalAddress': [],
        'Analytics': []
    }
    
    for result_set in all_results:
        for result in result_set:
            desc = result['description']
            if 'persona' in desc.lower() or 'person' in desc.lower():
                categories['Person'].append(result)
            elif 'organiz' in desc.lower():
                categories['Organization'].append(result)
            elif 'contacto' in desc.lower() or 'contact' in desc.lower():
                categories['ContactDetail'].append(result)
            elif 'perfil' in desc.lower() or 'profile' in desc.lower():
                categories['IndividualProfile'].append(result)
            elif 'direcci' in desc.lower() or 'address' in desc.lower():
                categories['PhysicalAddress'].append(result)
            else:
                categories['Analytics'].append(result)
    
    # Resumen por categoría
    for category, results in categories.items():
        if results:
            avg_times = [r['avg_time'] for r in results]
            avg_overall = statistics.mean(avg_times)
            print(f"\n🎯 {category}:")
            print(f"   Pruebas ejecutadas: {len(results)}")
            print(f"   Tiempo promedio: {avg_overall*1000:.2f}ms")
            print(f"   Consulta más rápida: {min(avg_times)*1000:.2f}ms")
            print(f"   Consulta más lenta: {max(avg_times)*1000:.2f}ms")
    
    # Top 5 consultas más rápidas
    all_flat = [r for result_set in all_results for r in result_set]
    fastest = sorted(all_flat, key=lambda x: x['avg_time'])[:5]
    
    print(f"\n🚀 TOP 5 CONSULTAS MÁS RÁPIDAS:")
    for i, result in enumerate(fastest, 1):
        print(f"   {i}. {result['description']}: {result['avg_time']*1000:.2f}ms")
    
    # Top 5 consultas más lentas
    slowest = sorted(all_flat, key=lambda x: x['avg_time'], reverse=True)[:5]
    
    print(f"\n🐌 TOP 5 CONSULTAS MÁS LENTAS:")
    for i, result in enumerate(slowest, 1):
        print(f"   {i}. {result['description']}: {result['avg_time']*1000:.2f}ms")
    
    # Resumen general
    overall_avg = statistics.mean([r['avg_time'] for r in all_flat])
    print(f"\n📊 RESUMEN GENERAL:")
    print(f"   Total de pruebas: {len(all_flat)}")
    print(f"   Tiempo promedio general: {overall_avg*1000:.2f}ms")
    print(f"   Consultas < 50ms: {len([r for r in all_flat if r['avg_time'] < 0.05])}")
    print(f"   Consultas < 100ms: {len([r for r in all_flat if r['avg_time'] < 0.1])}")
    print(f"   Consultas > 500ms: {len([r for r in all_flat if r['avg_time'] > 0.5])}")

def check_data_volume():
    """Verifica el volumen de datos disponible para testing"""
    print("📊 VERIFICANDO VOLUMEN DE DATOS")
    print("="*50)
    
    counts = {
        'Personas': Person.objects.count(),
        'Organizaciones': Organization.objects.count(),
        'Contactos': ContactDetail.objects.count(),
        'Perfiles': IndividualProfile.objects.count(),
        'Direcciones': PhysicalAddress.objects.count()
    }
    
    for model, count in counts.items():
        status = "✅" if count > 50 else "⚠️" if count > 10 else "❌"
        print(f"   {status} {model}: {count:,}")
    
    total_records = sum(counts.values())
    print(f"\n📈 Total de registros: {total_records:,}")
    
    if total_records < 500:
        print("\n⚠️  ADVERTENCIA: Pocos datos para testing confiable.")
        print("   Considera ejecutar create_test_data.py primero.")
        return False
    
    print("\n✅ Volumen de datos adecuado para testing de performance.")
    return True

def main():
    """Función principal para ejecutar todas las pruebas"""
    start_time = time.time()
    print("🚀 INICIANDO PRUEBAS DE PERFORMANCE - ENTITIES")
    print("="*70)
    print(f"🕐 Inicio: {timezone.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Verificar volumen de datos
    if not check_data_volume():
        print("❌ Terminando pruebas por falta de datos.")
        return
    
    print()
    
    try:
        # Ejecutar todas las pruebas
        all_results = []
        
        all_results.append(test_person_queries())
        all_results.append(test_organization_queries())
        all_results.append(test_contact_queries())
        all_results.append(test_profile_queries())
        all_results.append(test_address_queries())
        all_results.append(test_complex_analytics())
        
        # Generar reporte final
        generate_performance_report(all_results)
        
        end_time = time.time()
        duration = end_time - start_time
        
        print(f"\n⏱️  TIEMPO TOTAL DE TESTING: {duration:.2f} segundos")
        print(f"🕐 Fin: {timezone.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("\n✅ PRUEBAS DE PERFORMANCE COMPLETADAS!")
        
    except Exception as e:
        print(f"❌ Error durante las pruebas: {str(e)}")
        raise

if __name__ == "__main__":
    main()
