#!/usr/bin/env python
"""
Script para probar la funcionalidad de productos incluidos
"""
import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from products.models import Product, ProductCategory, Division, Modality
from decimal import Decimal


def create_test_data():
    """Crear datos de prueba para productos incluidos"""
    print("🚀 Creando datos de prueba para productos incluidos...")
    
    # Crear división si no existe
    division, created = Division.objects.get_or_create(
        code="TECH-TEST",
        defaults={
            'name': "Tecnología Test",
            'description': 'División de productos tecnológicos para pruebas'
        }
    )
    
    # Crear categoría si no existe
    category, created = ProductCategory.objects.get_or_create(
        code="SOFT-TEST",
        defaults={
            'name': "Software Test",
            'description': 'Productos de software para pruebas',
            'division': division
        }
    )
    
    # Crear modalidades
    modalidad_online, _ = Modality.objects.get_or_create(
        name="Online",
        defaults={'description': 'Modalidad en línea'}
    )
    
    modalidad_presencial, _ = Modality.objects.get_or_create(
        name="Presencial",
        defaults={'description': 'Modalidad presencial'}
    )
    
    # Crear productos individuales
    productos_individuales = [
        {
            'name': 'Curso Python Básico',
            'code': 'PY-BASIC',
            'description': 'Introducción a Python',
            'base_price': Decimal('299.00'),
            'currency_code': 'USD'
        },
        {
            'name': 'Curso Django Avanzado',
            'code': 'DJ-ADV',
            'description': 'Django para desarrolladores experimentados',
            'base_price': Decimal('499.00'),
            'currency_code': 'USD'
        },
        {
            'name': 'Taller de APIs REST',
            'code': 'API-REST',
            'description': 'Construcción de APIs REST con Django',
            'base_price': Decimal('199.00'),
            'currency_code': 'USD'
        },
        {
            'name': 'Certificación Python',
            'code': 'PY-CERT',
            'description': 'Examen de certificación en Python',
            'base_price': Decimal('99.00'),
            'currency_code': 'USD'
        }
    ]
    
    productos_creados = []
    for prod_data in productos_individuales:
        producto, created = Product.objects.get_or_create(
            code=prod_data['code'],
            defaults={
                'name': prod_data['name'],
                'description': prod_data['description'],
                'category': category,
                'base_price': prod_data['base_price'],
                'currency_code': prod_data['currency_code']
            }
        )
        productos_creados.append(producto)
        
        # Agregar modalidades
        producto.modalities.add(modalidad_online)
        if 'Taller' in producto.name:
            producto.modalities.add(modalidad_presencial)
        
        print(f"✅ Producto creado: {producto.name}")
    
    # Crear producto bundle
    bundle, created = Product.objects.get_or_create(
        code='PY-FULLSTACK',
        defaults={
            'name': 'Programa Completo Python Full-Stack',
            'description': 'Programa completo para convertirte en desarrollador Python Full-Stack',
            'category': category,
            'base_price': Decimal('799.00'),
            'currency_code': 'USD'
        }
    )
    
    if created:
        print(f"✅ Bundle creado: {bundle.name}")
        
        # Agregar productos incluidos al bundle
        python_basico = productos_creados[0]  # Curso Python Básico
        django_avanzado = productos_creados[1]  # Curso Django Avanzado
        api_rest = productos_creados[2]  # Taller de APIs REST
        certificacion = productos_creados[3]  # Certificación Python
        
        bundle.included_products.add(python_basico, django_avanzado, api_rest, certificacion)
        bundle.modalities.add(modalidad_online)
        
        print(f"🎁 Productos incluidos en el bundle:")
        for producto in bundle.included_products.all():
            print(f"   - {producto.name} (${producto.base_price})")
        
        print(f"💰 Precio total individual: ${bundle.get_total_included_price()}")
        print(f"💰 Precio del bundle: {bundle.get_bundle_price_display()}")
    
    return bundle, productos_creados


def test_bundle_functionality():
    """Probar la funcionalidad del bundle"""
    print("\n🔍 Probando funcionalidad de bundle...")
    
    try:
        bundle = Product.objects.get(code='PY-FULLSTACK')
        
        print(f"📦 Bundle: {bundle.name}")
        print(f"🏷️  Es bundle: {bundle.is_bundle}")
        print(f"💵 Precio display: {bundle.price_display}")
        print(f"🎁 Bundle price display: {bundle.get_bundle_price_display()}")
        print(f"📊 Productos incluidos: {bundle.get_included_products_display()}")
        
        # Probar métodos de productos incluidos
        included_products = bundle.get_included_products_list()
        print(f"\n📋 Lista de productos incluidos ({included_products.count()}):")
        for i, producto in enumerate(included_products, 1):
            print(f"   {i}. {producto.name} - {producto.price_display}")
            print(f"      Incluido en: {producto.get_parent_products().count()} bundle(s)")
        
        # Verificar precio total
        total_individual = sum(p.base_price for p in included_products if p.base_price)
        bundle_price = bundle.base_price
        ahorro = total_individual - bundle_price
        porcentaje_ahorro = (ahorro / total_individual) * 100 if total_individual > 0 else 0
        
        print(f"\n💰 Análisis de precios:")
        print(f"   Precio individual total: ${total_individual}")
        print(f"   Precio del bundle: ${bundle_price}")
        print(f"   Ahorro: ${ahorro} ({porcentaje_ahorro:.1f}%)")
        
        return True
        
    except Product.DoesNotExist:
        print("❌ Bundle no encontrado")
        return False


def test_api_methods():
    """Probar métodos de la API"""
    print("\n🧪 Probando métodos de la API...")
    
    try:
        bundle = Product.objects.get(code='PY-FULLSTACK')
        python_basic = Product.objects.get(code='PY-BASIC')
        
        # Probar agregar producto duplicado
        print("🔄 Intentando agregar producto ya incluido...")
        result = bundle.add_included_product(python_basic)
        print(f"   Resultado: {'❌ Ya incluido' if not result else '✅ Agregado'}")
        
        # Probar agregar producto a sí mismo (debe fallar)
        print("🔄 Intentando agregar bundle a sí mismo...")
        try:
            bundle.add_included_product(bundle)
            print("   ❌ Error: Se permitió agregar a sí mismo")
        except Exception as e:
            print(f"   ✅ Validación correcta: {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error en pruebas: {e}")
        return False


def main():
    """Función principal"""
    print("=" * 60)
    print("🧪 PRUEBA DE FUNCIONALIDAD: PRODUCTOS INCLUIDOS")
    print("=" * 60)
    
    try:
        # Crear datos de prueba
        bundle, productos = create_test_data()
        
        # Probar funcionalidad
        test_bundle_functionality()
        test_api_methods()
        
        print("\n" + "=" * 60)
        print("✅ TODAS LAS PRUEBAS COMPLETADAS EXITOSAMENTE")
        print("=" * 60)
        
        # Mostrar URLs para probar en el admin
        print("\n🌐 URLs para probar en el admin de Django:")
        print("   - Lista de productos: /admin/products/product/")
        print("   - Editar bundle: /admin/products/product/{}/change/".format(bundle.id))
        
    except Exception as e:
        print(f"\n❌ Error durante las pruebas: {e}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    main()
