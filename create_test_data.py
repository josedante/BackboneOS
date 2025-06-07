#!/usr/bin/env python
"""
Script para crear datos de prueba de our_institution
"""
import os
import sys
import django

# Configurar Django
sys.path.append('/app')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from our_institution.models import *

def create_test_data():
    print("🔄 Creando datos de prueba para our_institution...")
    
    # Limpiar datos existentes (solo para pruebas)
    OurOrganization.objects.all().delete()
    
    # Crear organización
    org = OurOrganization.objects.create(
        name="BackboneOS Corp",
        description="Organización principal de BackboneOS - Sistema CRM empresarial",
        is_active=True
    )
    print(f"✅ Organización creada: {org.name}")

    # Crear divisiones
    tech_division = Division.objects.create(
        organization=org,
        name="Tecnología e Innovación",
        code="TECH",
        description="División de tecnología, desarrollo y sistemas"
    )

    sales_division = Division.objects.create(
        organization=org,
        name="Comercial y Ventas",
        code="SALES",
        description="División comercial, ventas y desarrollo de negocio"
    )

    ops_division = Division.objects.create(
        organization=org,
        name="Operaciones",
        code="OPS",
        description="División de operaciones, recursos humanos y administración"
    )
    print(f"✅ Divisiones creadas: {Division.objects.count()}")

    # Crear sedes
    sede_lima = Seat.objects.create(
        organization=org,
        name="Oficina Principal Lima",
        code="LIM",
        description="Sede principal en Lima, Perú"
    )

    sede_bogota = Seat.objects.create(
        organization=org,
        name="Oficina Bogotá",
        code="BOG",
        description="Sede regional en Bogotá, Colombia"
    )
    print(f"✅ Sedes creadas: {Seat.objects.count()}")

    # Crear unidades en división de tecnología
    dev_unit = Unit.objects.create(
        organization=org,
        division=tech_division,
        name="Desarrollo de Software",
        code="DEV",
        description="Unidad de desarrollo de aplicaciones y sistemas"
    )

    devops_unit = Unit.objects.create(
        organization=org,
        division=tech_division,
        name="DevOps e Infraestructura",
        code="DEVOPS",
        description="Unidad de infraestructura y operaciones de desarrollo"
    )

    qa_unit = Unit.objects.create(
        organization=org,
        division=tech_division,
        name="Quality Assurance",
        code="QA",
        description="Unidad de control y aseguramiento de calidad",
        parent=dev_unit
    )

    # Crear unidades en división comercial
    sales_unit = Unit.objects.create(
        organization=org,
        division=sales_division,
        name="Ventas Directas",
        code="DIRECT_SALES",
        description="Unidad de ventas directas a empresas"
    )

    marketing_unit = Unit.objects.create(
        organization=org,
        division=sales_division,
        name="Marketing Digital",
        code="MARKETING",
        description="Unidad de marketing digital y generación de leads"
    )

    # Crear unidades en división de operaciones
    hr_unit = Unit.objects.create(
        organization=org,
        division=ops_division,
        name="Recursos Humanos",
        code="HR",
        description="Unidad de gestión de talento humano"
    )

    finance_unit = Unit.objects.create(
        organization=org,
        division=ops_division,
        name="Finanzas y Contabilidad",
        code="FINANCE",
        description="Unidad de gestión financiera y contable"
    )
    print(f"✅ Unidades creadas: {Unit.objects.count()}")

    # Crear equipos en tecnología
    backend_team = Team.objects.create(
        organization=org,
        division=tech_division,
        name="Equipo Backend",
        code="BACKEND",
        description="Equipo de desarrollo backend Python/Django"
    )

    frontend_team = Team.objects.create(
        organization=org,
        division=tech_division,
        name="Equipo Frontend",
        code="FRONTEND", 
        description="Equipo de desarrollo frontend Nuxt.js/Vue"
    )

    mobile_team = Team.objects.create(
        organization=org,
        division=tech_division,
        name="Equipo Mobile",
        code="MOBILE",
        description="Equipo de desarrollo de aplicaciones móviles"
    )

    # Crear equipos en ventas
    enterprise_team = Team.objects.create(
        organization=org,
        division=sales_division,
        name="Ventas Empresariales",
        code="ENTERPRISE",
        description="Equipo especializado en clientes empresariales"
    )

    smb_team = Team.objects.create(
        organization=org,
        division=sales_division,
        name="SMB Sales",
        code="SMB",
        description="Equipo de ventas para pequeñas y medianas empresas"
    )
    print(f"✅ Equipos creados: {Team.objects.count()}")

    # Crear posiciones
    positions_data = [
        # Tecnología
        (dev_unit, "Arquitecto de Software", "ARCH", "Arquitecto senior de sistemas"),
        (dev_unit, "Senior Backend Developer", "SR_BACKEND", "Desarrollador backend senior"),
        (dev_unit, "Senior Frontend Developer", "SR_FRONTEND", "Desarrollador frontend senior"),
        (dev_unit, "Full Stack Developer", "FULLSTACK", "Desarrollador full stack"),
        (qa_unit, "QA Engineer", "QA_ENG", "Ingeniero de calidad de software"),
        (qa_unit, "Test Automation Engineer", "QA_AUTO", "Ingeniero de automatización de pruebas"),
        (devops_unit, "DevOps Engineer", "DEVOPS_ENG", "Ingeniero de DevOps"),
        (devops_unit, "Cloud Infrastructure Engineer", "CLOUD_ENG", "Ingeniero de infraestructura en nube"),
        
        # Ventas
        (sales_unit, "Director Comercial", "SALES_DIR", "Director de ventas y desarrollo comercial"),
        (sales_unit, "Account Executive", "ACCOUNT_EXEC", "Ejecutivo de cuentas empresariales"),
        (sales_unit, "Sales Development Representative", "SDR", "Representante de desarrollo de ventas"),
        (marketing_unit, "Marketing Manager", "MARKETING_MGR", "Gerente de marketing digital"),
        (marketing_unit, "Growth Hacker", "GROWTH", "Especialista en crecimiento y adquisición"),
        
        # Operaciones
        (hr_unit, "Head of People", "HR_HEAD", "Jefe de recursos humanos"),
        (hr_unit, "Talent Acquisition Specialist", "TALENT_ACQ", "Especialista en adquisición de talento"),
        (finance_unit, "CFO", "CFO", "Director financiero"),
        (finance_unit, "Financial Analyst", "FIN_ANALYST", "Analista financiero"),
    ]

    for unit, name, code, description in positions_data:
        Position.objects.create(
            organization=org,
            unit=unit,
            name=name,
            code=code,
            description=description
        )
    print(f"✅ Posiciones creadas: {Position.objects.count()}")

    # Mostrar resumen
    print("\n📊 RESUMEN DE DATOS CREADOS:")
    print(f"├── Organización: {org.name}")
    print(f"├── Divisiones: {Division.objects.count()}")
    print(f"├── Sedes: {Seat.objects.count()}")
    print(f"├── Unidades: {Unit.objects.count()}")
    print(f"├── Equipos: {Team.objects.count()}")
    print(f"└── Posiciones: {Position.objects.count()}")
    
    # Mostrar estructura jerárquica
    print("\n🏢 ESTRUCTURA ORGANIZACIONAL:")
    for division in Division.objects.all():
        print(f"\n📁 {division.name} ({division.code})")
        print(f"   ├── Unidades: {division.units_count}")
        print(f"   ├── Equipos: {division.teams_count}")
        print(f"   └── Posiciones: {division.positions_count}")
        
        for unit in division.units.filter(parent__isnull=True):
            print(f"   📂 {unit.name} ({unit.code})")
            if unit.children.exists():
                for child in unit.children.all():
                    print(f"      📄 {child.name} ({child.code})")

    print("\n✅ ¡Datos de prueba creados exitosamente!")

if __name__ == "__main__":
    create_test_data()
