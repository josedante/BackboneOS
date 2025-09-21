# Custom migration to fix index naming issues after field type conversion

from django.db import migrations, connection


def check_and_rename_indexes(apps, schema_editor):
    """
    Check if indexes exist and rename them if they do.
    This handles the case where indexes were recreated with different names
    when fields were converted from CharField to ForeignKey.
    """
    with connection.cursor() as cursor:
        # List of index renames to attempt
        index_renames = [
            ('entities_pe_gender_89874f_idx', 'entities_pe_gender__522465_idx'),
            ('entities_pe_marital_e1e6f0_idx', 'entities_pe_marital_32e17d_idx'),
            ('entities_pe_is_acti_f517d0_idx', 'entities_pe_is_acti_11ce92_idx'),
            ('entities_pe_is_acti_60b273_idx', 'entities_pe_is_acti_8e6b7f_idx'),
            ('entities_pe_gender_e455c8_idx', 'entities_pe_gender__633dfc_idx'),
            ('entities_pe_marital_a02f17_idx', 'entities_pe_marital_2f7a66_idx'),
        ]
        
        for old_name, new_name in index_renames:
            try:
                # Check if the old index exists
                cursor.execute("""
                    SELECT indexname FROM pg_indexes 
                    WHERE indexname = %s
                """, [old_name])
                
                if cursor.fetchone():
                    # Index exists, rename it
                    cursor.execute(f'ALTER INDEX "{old_name}" RENAME TO "{new_name}"')
                    print(f"Renamed index {old_name} to {new_name}")
                else:
                    print(f"Index {old_name} does not exist, skipping rename")
                    
            except Exception as e:
                print(f"Error handling index {old_name}: {e}")
                # Continue with other indexes even if one fails


def reverse_check_and_rename_indexes(apps, schema_editor):
    """
    Reverse the index renames.
    """
    with connection.cursor() as cursor:
        # List of index renames to reverse
        index_renames = [
            ('entities_pe_gender__522465_idx', 'entities_pe_gender_89874f_idx'),
            ('entities_pe_marital_32e17d_idx', 'entities_pe_marital_e1e6f0_idx'),
            ('entities_pe_is_acti_11ce92_idx', 'entities_pe_is_acti_f517d0_idx'),
            ('entities_pe_is_acti_8e6b7f_idx', 'entities_pe_is_acti_60b273_idx'),
            ('entities_pe_gender__633dfc_idx', 'entities_pe_gender_e455c8_idx'),
            ('entities_pe_marital_2f7a66_idx', 'entities_pe_marital_a02f17_idx'),
        ]
        
        for new_name, old_name in index_renames:
            try:
                # Check if the new index exists
                cursor.execute("""
                    SELECT indexname FROM pg_indexes 
                    WHERE indexname = %s
                """, [new_name])
                
                if cursor.fetchone():
                    # Index exists, rename it back
                    cursor.execute(f'ALTER INDEX "{new_name}" RENAME TO "{old_name}"')
                    print(f"Renamed index {new_name} back to {old_name}")
                else:
                    print(f"Index {new_name} does not exist, skipping reverse rename")
                    
            except Exception as e:
                print(f"Error handling index {new_name}: {e}")


class Migration(migrations.Migration):

    dependencies = [
        ('entities', '0006_convert_gender_marital_status_to_foreign_keys'),
    ]

    operations = [
        migrations.RunPython(
            check_and_rename_indexes,
            reverse_check_and_rename_indexes,
        ),
    ]
