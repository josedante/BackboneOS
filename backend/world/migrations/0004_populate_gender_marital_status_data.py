# Generated migration to populate initial Gender and MaritalStatus data

from django.db import migrations


def populate_initial_data(apps, schema_editor):
    """
    Populate initial Gender and MaritalStatus records
    """
    Gender = apps.get_model('world', 'Gender')
    MaritalStatus = apps.get_model('world', 'MaritalStatus')
    
    # Create Gender records
    genders_data = [
        {'name': 'Masculino', 'code': 'M', 'description': 'Género masculino', 'display_order': 1},
        {'name': 'Femenino', 'code': 'F', 'description': 'Género femenino', 'display_order': 2},
        {'name': 'No definido', 'code': 'UD', 'description': 'Género no especificado', 'display_order': 3},
        {'name': 'No binario', 'code': 'NB', 'description': 'Persona no binaria', 'display_order': 4},
        {'name': 'Género fluido', 'code': 'GF', 'description': 'Género fluido', 'display_order': 5},
        {'name': 'Agénero', 'code': 'AG', 'description': 'Sin género', 'display_order': 6},
        {'name': 'Prefiero no decir', 'code': 'PND', 'description': 'Prefiero no especificar', 'display_order': 7},
    ]
    
    for gender_data in genders_data:
        gender, created = Gender.objects.get_or_create(
            code=gender_data['code'],
            defaults=gender_data
        )
        if created:
            print(f"Created gender: {gender.name}")
    
    # Create MaritalStatus records
    marital_statuses_data = [
        {'name': 'Soltero', 'code': 'SG', 'description': 'Estado civil soltero', 'display_order': 1},
        {'name': 'Casado', 'code': 'MR', 'description': 'Estado civil casado', 'display_order': 2},
        {'name': 'Divorciado', 'code': 'DV', 'description': 'Estado civil divorciado', 'display_order': 3},
        {'name': 'Separado', 'code': 'SP', 'description': 'Estado civil separado', 'display_order': 4},
        {'name': 'Viudo', 'code': 'WD', 'description': 'Estado civil viudo', 'display_order': 5},
        {'name': 'Conviviente', 'code': 'CH', 'description': 'Estado civil conviviente', 'display_order': 6},
        {'name': 'No definido', 'code': 'UD', 'description': 'Estado civil no especificado', 'display_order': 7},
        {'name': 'Unión libre', 'code': 'UL', 'description': 'Unión libre o concubinato', 'display_order': 8},
    ]
    
    for status_data in marital_statuses_data:
        marital_status, created = MaritalStatus.objects.get_or_create(
            code=status_data['code'],
            defaults=status_data
        )
        if created:
            print(f"Created marital status: {marital_status.name}")


def reverse_populate_initial_data(apps, schema_editor):
    """
    Remove the initial data (for rollback purposes)
    """
    Gender = apps.get_model('world', 'Gender')
    MaritalStatus = apps.get_model('world', 'MaritalStatus')
    
    # Remove all Gender and MaritalStatus records
    Gender.objects.all().delete()
    MaritalStatus.objects.all().delete()
    
    print("Removed all Gender and MaritalStatus records")


class Migration(migrations.Migration):

    dependencies = [
        ('world', '0003_add_gender_marital_status_models'),
    ]

    operations = [
        migrations.RunPython(
            code=populate_initial_data,
            reverse_code=reverse_populate_initial_data,
        ),
    ]
