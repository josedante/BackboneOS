# Generated migration for converting gender and marital_status to ForeignKeys

from django.db import migrations, models
import django.db.models.deletion


def populate_new_fields(apps, schema_editor):
    """
    Populate the new ForeignKey fields with data from old CharField choices
    """
    Person = apps.get_model('entities', 'Person')
    Gender = apps.get_model('world', 'Gender')
    MaritalStatus = apps.get_model('world', 'MaritalStatus')
    
    # Create Gender records from old choices
    gender_mapping = {
        'M': {'name': 'Masculino', 'code': 'M', 'display_order': 1},
        'F': {'name': 'Femenino', 'code': 'F', 'display_order': 2},
        'UD': {'name': 'No definido', 'code': 'UD', 'display_order': 3},
    }
    
    created_genders = {}
    for old_code, gender_data in gender_mapping.items():
        gender, created = Gender.objects.get_or_create(
            code=gender_data['code'],
            defaults=gender_data
        )
        created_genders[old_code] = gender
        if created:
            print(f"Created gender: {gender.name}")
    
    # Create MaritalStatus records from old choices
    marital_status_mapping = {
        'SG': {'name': 'Soltero', 'code': 'SG', 'display_order': 1},
        'MR': {'name': 'Casado', 'code': 'MR', 'display_order': 2},
        'DV': {'name': 'Divorciado', 'code': 'DV', 'display_order': 3},
        'SP': {'name': 'Separado', 'code': 'SP', 'display_order': 4},
        'WD': {'name': 'Viudo', 'code': 'WD', 'display_order': 5},
        'CH': {'name': 'Conviviente', 'code': 'CH', 'display_order': 6},
        'UD': {'name': 'No definido', 'code': 'UD', 'display_order': 7},
    }
    
    created_marital_statuses = {}
    for old_code, status_data in marital_status_mapping.items():
        marital_status, created = MaritalStatus.objects.get_or_create(
            code=status_data['code'],
            defaults=status_data
        )
        created_marital_statuses[old_code] = marital_status
        if created:
            print(f"Created marital status: {marital_status.name}")
    
    # Update Person records to use new ForeignKey fields
    updated_count = 0
    for person in Person.objects.all():
        updated = False
        
        # Update gender
        if person.gender and person.gender in created_genders:
            person.gender_new = created_genders[person.gender]
            updated = True
        
        # Update marital_status
        if person.marital_status and person.marital_status in created_marital_statuses:
            person.marital_status_new = created_marital_statuses[person.marital_status]
            updated = True
        
        if updated:
            person.save()
            updated_count += 1
    
    print(f"Updated {updated_count} Person records with new ForeignKey relationships")


def reverse_populate_new_fields(apps, schema_editor):
    """
    Reverse the data migration (for rollback purposes)
    """
    Person = apps.get_model('entities', 'Person')
    Gender = apps.get_model('world', 'Gender')
    MaritalStatus = apps.get_model('world', 'MaritalStatus')
    
    # Create reverse mapping
    gender_reverse_mapping = {}
    for gender in Gender.objects.all():
        gender_reverse_mapping[gender.id] = gender.code
    
    marital_status_reverse_mapping = {}
    for marital_status in MaritalStatus.objects.all():
        marital_status_reverse_mapping[marital_status.id] = marital_status.code
    
    # Update Person records back to old CharField values
    updated_count = 0
    for person in Person.objects.all():
        updated = False
        
        # Update gender back to old format
        if person.gender_new and person.gender_new.id in gender_reverse_mapping:
            person.gender = gender_reverse_mapping[person.gender_new.id]
            updated = True
        
        # Update marital_status back to old format
        if person.marital_status_new and person.marital_status_new.id in marital_status_reverse_mapping:
            person.marital_status = marital_status_reverse_mapping[person.marital_status_new.id]
            updated = True
        
        if updated:
            person.save()
            updated_count += 1
    
    print(f"Reverted {updated_count} Person records back to CharField values")


class Migration(migrations.Migration):

    dependencies = [
        ('world', '0003_add_gender_marital_status_models'),
        ('entities', '0005_rename_person_name_fields'),
    ]

    operations = [
        # Step 1: Add new ForeignKey fields (nullable initially)
        migrations.AddField(
            model_name='person',
            name='gender_new',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='world.gender'),
        ),
        migrations.AddField(
            model_name='person',
            name='marital_status_new',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='world.maritalstatus'),
        ),
        
        # Step 2: Data migration to populate new fields
        migrations.RunPython(
            code=populate_new_fields,
            reverse_code=reverse_populate_new_fields,
        ),
        
        # Step 3: Remove old CharField columns
        migrations.RemoveField(
            model_name='person',
            name='gender',
        ),
        migrations.RemoveField(
            model_name='person',
            name='marital_status',
        ),
        
        # Step 4: Rename new fields to original names
        migrations.RenameField(
            model_name='person',
            old_name='gender_new',
            new_name='gender',
        ),
        migrations.RenameField(
            model_name='person',
            old_name='marital_status_new',
            new_name='marital_status',
        ),
    ]
