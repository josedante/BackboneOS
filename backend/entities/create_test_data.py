#!/usr/bin/env python3
"""
Script para crear datos de prueba masivos para testing de performance
en la aplicación entities.

Uso:
    python manage.py shell < entities/create_test_data.py
    
O desde shell de Django:
    exec(open('entities/create_test_data.py').read())
"""

import random
import time
from datetime import datetime, timedelta, date
from django.db import transaction
from django.utils import timezone

# Importar modelos
from entities.models import Person, Organization, ContactDetail, IndividualProfile, PhysicalAddress
from world.models import (
    Country, PersonalIDType, OrganizationalIDType, OrganizationType,
    Industry, FunctionOrResponsibility, Skill, AcademicDegree
)

# Configuración
BATCH_SIZE = 100
NUM_PERSONS = 1000
NUM_ORGANIZATIONS = 200
CONTACTS_PER_ENTITY = 2
PROFILES_PERCENTAGE = 0.8  # 80% de personas tendrán perfil
ADDRESSES_PER_ENTITY = 1.5

def get_random_choice(choices):
    """Obtiene una opción aleatoria de las choices de Django"""
    return random.choice([choice[0] for choice in choices])

def get_random_date(start_year=1950, end_year=2005):
    """Genera una fecha aleatoria entre años dados"""
    start_date = date(start_year, 1, 1)
    end_date = date(end_year, 12, 31)
    days_between = (end_date - start_date).days
    random_days = random.randrange(days_between)
    return start_date + timedelta(days=random_days)

def create_base_data():
    """Crea datos base necesarios desde world app"""
    print("🌍 Verificando datos base de world app...")
    
    # Verificar que tenemos datos básicos
    countries_count = Country.objects.count()
    industries_count = Industry.objects.count()
    skills_count = Skill.objects.count()
    
    print(f"  - Países: {countries_count}")
    print(f"  - Industrias: {industries_count}")  
    print(f"  - Habilidades: {skills_count}")
    
    if countries_count < 5:
        print("⚠️  Pocos países disponibles. Considera ejecutar populate_world_data.py primero")
    
    return {
        'countries': list(Country.objects.filter(is_active=True)[:20]),
        'personal_id_types': list(PersonalIDType.objects.filter(is_active=True)),
        'org_id_types': list(OrganizationalIDType.objects.filter(is_active=True)),
        'org_types': list(OrganizationType.objects.filter(is_active=True)),
        'industries': list(Industry.objects.filter(is_active=True)[:50]),
        'functions': list(FunctionOrResponsibility.objects.filter(is_active=True)[:30]),
        'skills': list(Skill.objects.filter(is_active=True)[:100]),
        'academic_degrees': list(AcademicDegree.objects.filter(is_active=True))
    }

def create_test_persons(base_data, num_persons=NUM_PERSONS):
    """Crea personas de prueba en lotes"""
    print(f"👥 Creando {num_persons} personas de prueba...")
    
    # Nombres comunes para testing
    first_names = [
        'Ana', 'María', 'Carmen', 'José', 'Francisco', 'David', 'Antonio',
        'Manuel', 'Daniel', 'Carlos', 'Miguel', 'Rafael', 'Pedro', 'Ángel',
        'Laura', 'Elena', 'Sara', 'Lucía', 'Paula', 'Cristina', 'Marta',
        'Alba', 'Julia', 'Patricia', 'Claudia', 'Andrea', 'Raquel', 'Silvia'
    ]
    
    fathers_names = [
        'García', 'González', 'Rodríguez', 'Fernández', 'López', 'Martínez',
        'Sánchez', 'Pérez', 'Gómez', 'Martín', 'Jiménez', 'Ruiz', 'Hernández',
        'Díaz', 'Moreno', 'Álvarez', 'Muñoz', 'Romero', 'Alonso', 'Gutiérrez',
        'Navarro', 'Torres', 'Domínguez', 'Vázquez', 'Ramos', 'Gil', 'Ramírez'
    ]
    
    created_count = 0
    
    for batch_start in range(0, num_persons, BATCH_SIZE):
        batch_end = min(batch_start + BATCH_SIZE, num_persons)
        batch_persons = []
        
        for i in range(batch_start, batch_end):
            person = Person(
                first_name=random.choice(first_names),
                middle_name=random.choice(first_names) if random.random() < 0.3 else '',
                fathers_name=random.choice(fathers_names),
                mothers_name=random.choice(fathers_names) if random.random() < 0.8 else '',
                gender=get_random_choice(Person._meta.get_field('gender').choices),
                birthday=get_random_date() if random.random() < 0.9 else None,
                marital_status=get_random_choice(Person._meta.get_field('marital_status').choices),
                country_of_nationality=random.choice(base_data['countries']) if base_data['countries'] else None,
                id_type=random.choice(base_data['personal_id_types']) if base_data['personal_id_types'] else None,
                id_number=f"{random.randint(10000000, 99999999)}" if random.random() < 0.8 else '',
                is_active=random.random() < 0.95  # 95% activos
            )
            batch_persons.append(person)
        
        # Crear en lote
        with transaction.atomic():
            Person.objects.bulk_create(batch_persons, ignore_conflicts=True)
            created_count += len(batch_persons)
        
        print(f"  ✅ Creadas {created_count}/{num_persons} personas...")
    
    print(f"🎉 {created_count} personas creadas exitosamente")
    return Person.objects.filter(is_active=True).count()

def create_test_organizations(base_data, num_orgs=NUM_ORGANIZATIONS):
    """Crea organizaciones de prueba"""
    print(f"🏢 Creando {num_orgs} organizaciones de prueba...")
    
    company_prefixes = ['Tecnología', 'Sistemas', 'Servicios', 'Consultoría', 'Desarrollo']
    company_suffixes = ['SAS', 'SRL', 'SA', 'LTDA', 'Corp', 'Tech', 'Solutions', 'Group']
    company_types = ['Empresa', 'Compañía', 'Corporación', 'Sociedad', 'Firma']
    
    created_count = 0
    
    for batch_start in range(0, num_orgs, BATCH_SIZE):
        batch_end = min(batch_start + BATCH_SIZE, num_orgs)
        batch_orgs = []
        
        for i in range(batch_start, batch_end):
            name = f"{random.choice(company_prefixes)} {random.choice(company_types)} {random.choice(company_suffixes)}"
            
            org = Organization(
                name=name,
                legal_name=f"{name} {random.choice(company_suffixes)}" if random.random() < 0.7 else '',
                org_type=random.choice(base_data['org_types']) if base_data['org_types'] else None,
                industry=random.choice(base_data['industries']) if base_data['industries'] else None,
                id_type=random.choice(base_data['org_id_types']) if base_data['org_id_types'] else None,
                id_number=f"9{random.randint(10000000, 99999999)}",
                main_address=f"Calle {random.randint(1, 100)} #{random.randint(1, 50)}-{random.randint(1, 99)}",
                country=random.choice(base_data['countries']) if base_data['countries'] else None,
                is_active=random.random() < 0.95
            )
            batch_orgs.append(org)
        
        # Crear en lote
        with transaction.atomic():
            Organization.objects.bulk_create(batch_orgs, ignore_conflicts=True)
            created_count += len(batch_orgs)
        
        print(f"  ✅ Creadas {created_count}/{num_orgs} organizaciones...")
    
    print(f"🎉 {created_count} organizaciones creadas exitosamente")
    return Organization.objects.filter(is_active=True).count()

def create_test_contacts():
    """Crea contactos para personas y organizaciones"""
    print("📞 Creando contactos de prueba...")
    
    domains = ['gmail.com', 'hotmail.com', 'yahoo.com', 'outlook.com', 'empresa.com', 'test.com']
    
    created_count = 0
    
    # Contactos para personas
    persons = Person.objects.filter(is_active=True)
    for person in persons:
        num_contacts = random.randint(1, CONTACTS_PER_ENTITY)
        
        for i in range(num_contacts):
            contact = ContactDetail(
                person=person,
                email=f"{person.first_name.lower()}.{person.fathers_name.lower()}{random.randint(1, 999)}@{random.choice(domains)}",
                phone=f"+57{random.randint(3000000000, 3999999999)}" if random.random() < 0.8 else '',
                is_primary=(i == 0),  # Primer contacto es principal
                verified=random.random() < 0.7,
                is_active=random.random() < 0.95
            )
            contact.save()
            created_count += 1
    
    # Contactos para organizaciones
    organizations = Organization.objects.filter(is_active=True)
    for org in organizations:
        num_contacts = random.randint(1, CONTACTS_PER_ENTITY)
        
        for i in range(num_contacts):
            contact = ContactDetail(
                organization=org,
                email=f"info{i}@{org.name.lower().replace(' ', '')}.com",
                phone=f"+57{random.randint(6000000, 6999999)}{random.randint(100, 999)}" if random.random() < 0.9 else '',
                is_primary=(i == 0),
                verified=random.random() < 0.8,
                is_active=random.random() < 0.95
            )
            contact.save()
            created_count += 1
    
    print(f"🎉 {created_count} contactos creados exitosamente")
    return created_count

def create_test_profiles(base_data):
    """Crea perfiles individuales para personas"""
    print("👤 Creando perfiles individuales...")
    
    persons = Person.objects.filter(is_active=True)
    total_persons = persons.count()
    target_profiles = int(total_persons * PROFILES_PERCENTAGE)
    
    selected_persons = random.sample(list(persons), target_profiles)
    created_count = 0
    
    for batch_start in range(0, len(selected_persons), BATCH_SIZE):
        batch_end = min(batch_start + BATCH_SIZE, len(selected_persons))
        batch_profiles = []
        
        for person in selected_persons[batch_start:batch_end]:
            profile = IndividualProfile(
                person=person,
                academic_degree=random.choice(base_data['academic_degrees']) if base_data['academic_degrees'] else None,
                accepts_privacy_policy=random.random() < 0.9,
                allows_marketing=random.random() < 0.6,
                preferred_contact_medium=get_random_choice(
                    IndividualProfile._meta.get_field('preferred_contact_medium').choices
                ),
                is_active=random.random() < 0.95
            )
            batch_profiles.append(profile)
        
        # Crear perfiles en lote
        with transaction.atomic():
            created_profiles = IndividualProfile.objects.bulk_create(batch_profiles, ignore_conflicts=True)
            created_count += len(created_profiles)
            
            # Agregar relaciones ManyToMany
            for i, profile in enumerate(created_profiles):
                if base_data['industries']:
                    industries = random.sample(
                        base_data['industries'], 
                        min(random.randint(1, 3), len(base_data['industries']))
                    )
                    profile.industries.set(industries)
                
                if base_data['skills']:
                    skills = random.sample(
                        base_data['skills'],
                        min(random.randint(2, 8), len(base_data['skills']))
                    )
                    profile.skills.set(skills)
                
                if base_data['functions']:
                    functions = random.sample(
                        base_data['functions'],
                        min(random.randint(1, 2), len(base_data['functions']))
                    )
                    profile.functions.set(functions)
        
        print(f"  ✅ Creados {created_count}/{target_profiles} perfiles...")
    
    print(f"🎉 {created_count} perfiles individuales creados exitosamente")
    return created_count

def create_test_addresses(base_data):
    """Crea direcciones físicas para entidades"""
    print("🏠 Creando direcciones físicas...")
    
    cities = ['Bogotá', 'Medellín', 'Cali', 'Barranquilla', 'Cartagena', 'Bucaramanga', 'Pereira', 'Manizales']
    
    created_count = 0
    
    # Direcciones para personas
    persons = Person.objects.filter(is_active=True)
    for person in persons:
        if random.random() < ADDRESSES_PER_ENTITY:
            address = PhysicalAddress(
                owner_person=person,
                address=f"Calle {random.randint(1, 200)} #{random.randint(1, 100)}-{random.randint(1, 200)}",
                address_extra=f"Apto {random.randint(101, 999)}" if random.random() < 0.4 else '',
                city=random.choice(cities),
                region_or_state='Colombia',
                country=random.choice(base_data['countries']) if base_data['countries'] else None,
                zip_code=f"{random.randint(10000, 99999)}" if random.random() < 0.6 else '',
                is_primary=True,
                use_for_billing=random.random() < 0.3,
                is_active=random.random() < 0.95
            )
            address.save()
            created_count += 1
    
    # Direcciones para organizaciones
    organizations = Organization.objects.filter(is_active=True)
    for org in organizations:
        # Direcciones principales
        address = PhysicalAddress(
            owner_org=org,
            address=f"Carrera {random.randint(1, 50)} #{random.randint(1, 100)}-{random.randint(1, 200)}",
            address_extra=f"Oficina {random.randint(100, 999)}" if random.random() < 0.7 else '',
            city=random.choice(cities),
            region_or_state='Colombia',
            country=random.choice(base_data['countries']) if base_data['countries'] else None,
            zip_code=f"{random.randint(10000, 99999)}",
            is_primary=True,
            use_for_billing=True,
            is_active=True
        )
        address.save()
        created_count += 1
        
        # Direcciones adicionales (30% de probabilidad)
        if random.random() < 0.3:
            address2 = PhysicalAddress(
                owner_org=org,
                address=f"Avenida {random.randint(1, 30)} #{random.randint(1, 100)}-{random.randint(1, 200)}",
                city=random.choice(cities),
                region_or_state='Colombia', 
                country=random.choice(base_data['countries']) if base_data['countries'] else None,
                is_primary=False,
                use_for_billing=False,
                is_active=True
            )
            address2.save()
            created_count += 1
    
    print(f"🎉 {created_count} direcciones creadas exitosamente")
    return created_count

def main():
    """Función principal para crear todos los datos de prueba"""
    start_time = time.time()
    print("🚀 Iniciando creación de datos de prueba para entities...")
    print(f"📊 Configuración:")
    print(f"  - Personas: {NUM_PERSONS}")
    print(f"  - Organizaciones: {NUM_ORGANIZATIONS}")
    print(f"  - Contactos por entidad: {CONTACTS_PER_ENTITY}")
    print(f"  - Porcentaje con perfil: {PROFILES_PERCENTAGE*100}%")
    print(f"  - Direcciones por entidad: {ADDRESSES_PER_ENTITY}")
    print()
    
    try:
        # 1. Obtener datos base
        base_data = create_base_data()
        
        # 2. Crear personas
        persons_created = create_test_persons(base_data, NUM_PERSONS)
        
        # 3. Crear organizaciones
        orgs_created = create_test_organizations(base_data, NUM_ORGANIZATIONS)
        
        # 4. Crear contactos
        contacts_created = create_test_contacts()
        
        # 5. Crear perfiles
        profiles_created = create_test_profiles(base_data)
        
        # 6. Crear direcciones
        addresses_created = create_test_addresses(base_data)
        
        # Resumen final
        end_time = time.time()
        duration = end_time - start_time
        
        print("\n" + "="*50)
        print("🎉 CREACIÓN DE DATOS COMPLETADA")
        print("="*50)
        print(f"⏱️  Tiempo total: {duration:.2f} segundos")
        print(f"👥 Personas creadas: {persons_created}")
        print(f"🏢 Organizaciones creadas: {orgs_created}")
        print(f"📞 Contactos creados: {contacts_created}")
        print(f"👤 Perfiles creados: {profiles_created}")
        print(f"🏠 Direcciones creadas: {addresses_created}")
        print()
        
        # Verificación final
        print("📊 VERIFICACIÓN FINAL:")
        print(f"  - Total personas activas: {Person.objects.filter(is_active=True).count()}")
        print(f"  - Total organizaciones activas: {Organization.objects.filter(is_active=True).count()}")
        print(f"  - Total contactos activos: {ContactDetail.objects.filter(is_active=True).count()}")
        print(f"  - Total perfiles activos: {IndividualProfile.objects.filter(is_active=True).count()}")
        print(f"  - Total direcciones activas: {PhysicalAddress.objects.filter(is_active=True).count()}")
        
        print("\n✅ Datos de prueba listos para testing de performance!")
        
    except Exception as e:
        print(f"❌ Error durante la creación de datos: {str(e)}")
        raise

if __name__ == "__main__":
    main()
