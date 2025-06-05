#!/usr/bin/env python
"""
Script para crear datos de prueba de divisiones y actualizar categorías existentes
"""
import os
import sys
import django

# Configurar Django
sys.path.append('/app')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from products.models import Division, ProductCategory

def create_divisions():
    """Crear divisiones de ejemplo"""
    divisions_data = [
        {
            'name': 'Tecnología y Desarrollo',
            'code': 'TECH',
            'description': 'División especializada en soluciones tecnológicas, desarrollo de software y transformación digital'
        },
        {
            'name': 'Consultoría Empresarial',
            'code': 'CONS',
            'description': 'División enfocada en consultoría estratégica, mejora de procesos y gestión organizacional'
        },
        {
            'name': 'Capacitación y Formación',
            'code': 'FORM',
            'description': 'División dedicada a programas de capacitación, talleres y desarrollo de competencias'
        },
        {
            'name': 'Marketing y Ventas',
            'code': 'MKTV',
            'description': 'División especializada en estrategias de marketing, ventas y desarrollo comercial'
        },
        {
            'name': 'Recursos Humanos',
            'code': 'RRHH',
            'description': 'División enfocada en gestión de talento, reclutamiento y desarrollo organizacional'
        }
    ]
    
    created_divisions = []
    for div_data in divisions_data:
        division, created = Division.objects.get_or_create(
            code=div_data['code'],
            defaults={
                'name': div_data['name'],
                'description': div_data['description']
            }
        )
        created_divisions.append(division)
        print(f"{'Creada' if created else 'Actualizada'} división: {division.name}")
    
    return created_divisions

def assign_categories_to_divisions():
    """Asignar categorías existentes a divisiones"""
    
    # Mapeo de categorías a divisiones (por código de división)
    category_division_mapping = {
        # Tecnología y Desarrollo
        'TECH': [
            'Desarrollo de Software',
            'Desarrollo Web',
            'Desarrollo Mobile',
            'DevOps',
            'Consultoría TI',
            'Infraestructura TI'
        ],
        
        # Consultoría Empresarial
        'CONS': [
            'Consultoría Estratégica',
            'Consultoría de Procesos',
            'Consultoría Organizacional',
            'Consultoría de Gestión'
        ],
        
        # Capacitación y Formación
        'FORM': [
            'Capacitación Técnica',
            'Capacitación Gerencial',
            'Talleres',
            'Cursos Online',
            'Certificaciones'
        ],
        
        # Marketing y Ventas
        'MKTV': [
            'Marketing Digital',
            'Marketing Estratégico',
            'Ventas B2B',
            'Ventas B2C',
            'Branding'
        ],
        
        # Recursos Humanos
        'RRHH': [
            'Reclutamiento',
            'Evaluación de Desempeño',
            'Desarrollo de Talento',
            'Gestión de Compensaciones'
        ]
    }
    
    updated_count = 0
    for division_code, category_names in category_division_mapping.items():
        try:
            division = Division.objects.get(code=division_code)
            
            for category_name in category_names:
                categories = ProductCategory.objects.filter(
                    name__icontains=category_name,
                    division__isnull=True  # Solo categorías sin división asignada
                )
                
                for category in categories:
                    category.division = division
                    category.save()
                    updated_count += 1
                    print(f"Asignada categoría '{category.name}' a división '{division.name}'")
                    
        except Division.DoesNotExist:
            print(f"División con código '{division_code}' no encontrada")
    
    print(f"\nTotal de categorías actualizadas: {updated_count}")

def main():
    print("=== Creando datos de divisiones ===")
    
    # Crear divisiones
    divisions = create_divisions()
    print(f"\nDivisiones disponibles: {len(divisions)}")
    
    # Asignar categorías existentes a divisiones
    print("\n=== Asignando categorías a divisiones ===")
    assign_categories_to_divisions()
    
    # Mostrar resumen
    print("\n=== Resumen final ===")
    for division in Division.objects.filter(is_active=True):
        categories_count = division.categories.filter(is_active=True).count()
        print(f"- {division.name} ({division.code}): {categories_count} categorías")

if __name__ == '__main__':
    main()
