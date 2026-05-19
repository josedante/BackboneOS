from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0002_remove_redundant_indexes'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='usersession',
            name='session_duration_minutes',
        ),
    ]
