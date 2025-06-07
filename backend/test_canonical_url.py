#!/usr/bin/env python
"""
Script para probar el campo canonical_url en los productos
"""
import os
import sys
import django

# Configuración de Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from products.models import Product, ProductCategory, Division
from decimal import Decimal

def test_canonical_url():
    """Prueba el campo canonical_url"""
    print("🧪 Probando campo canonical_url...")
    
    # Obtener o crear división de prueba con código único
    division, created = Division.objects.get_or_create(
        code='TECH-TEST',
        defaults={
            'name': 'Tecnología Test',
            'description': 'División de prueba para productos tecnológicos'
        }
    )
    if created:
        print(f"✅ División creada: {division.name}")
    else:
        print(f"📁 División existente: {division.name}")
    
    # Obtener o crear categoría de prueba
    category, created = ProductCategory.objects.get_or_create(
        code='WEB-TEST',
        defaults={
            'name': 'Desarrollo Web Test',
            'description': 'Categoría de prueba para desarrollo web',
            'division': division
        }
    )
    if created:
        print(f"✅ Categoría creada: {category.name}")
    else:
        print(f"📁 Categoría existente: {category.name}")
    
    # Crear productos de prueba
    products_data = [
        {
            'name': 'Curso de React Avanzado',
            'code': 'REACT-ADV-TEST',
            'description': 'Curso completo de React con hooks y context',
            'canonical_url': 'https://example.com/cursos/react-avanzado',
            'base_price': Decimal('299.99'),
            'category': category
        },
        {
            'name': 'Workshop de Node.js',
            'code': 'NODE-WS-TEST',
            'description': 'Workshop práctico de Node.js y Express',
            'canonical_url': 'https://example.com/workshops/nodejs',
            'base_price': Decimal('149.99'),
            'category': category
        },
        {
            'name': 'Consultoría Personalizada',
            'code': 'CONSULT-TEST',
            'description': 'Consultoría técnica personalizada',
            'canonical_url': None,  # Sin URL
            'base_price': Decimal('500.00'),
            'category': category
        }
    ]
    
    print("\n📦 Creando productos de prueba...")
    created_products = []
    
    for data in products_data:
        product, created = Product.objects.get_or_create(
            code=data['code'],
            defaults=data
        )
        if created:
            created_products.append(product)
            print(f"✅ Producto creado: {product.name}")
        else:
            print(f"📦 Producto existente: {product.name}")
    
    # Probar propiedades
    print("\n🔍 Probando propiedades...")
    all_products = Product.objects.filter(category=category)
    
    for product in all_products:
        print(f"\n📦 Producto: {product.name}")
        print(f"   🔗 URL Canónica: {product.canonical_url or 'Sin URL'}")
        print(f"   ✅ Tiene URL: {product.has_canonical_url}")
        print(f"   💰 Precio: {product.price_display}")
        print(f"   🎨 Personalizable: {product.is_customizable}")
    
    # Probar filtros
    print("\n🔍 Probando filtros...")
    products_with_url = Product.objects.filter(
        canonical_url__isnull=False
    ).exclude(canonical_url='')
    print(f"📊 Productos con URL canónica: {products_with_url.count()}")
    
    products_without_url = Product.objects.filter(
        canonical_url__isnull=True
    ) | Product.objects.filter(canonical_url='')
    print(f"📊 Productos sin URL canónica: {products_without_url.count()}")
    
    print("\n✅ Pruebas completadas exitosamente!")
    return True

if __name__ == "__main__":
    try:
        test_canonical_url()
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)
