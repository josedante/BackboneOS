import json
import os
from django.core.management.base import BaseCommand
from django.core.management import call_command
from interactions.models import Medium, Channel, ActionType, Action


class Command(BaseCommand):
    help = 'Carga datos iniciales para la aplicación interactions'

    def add_arguments(self, parser):
        parser.add_argument(
            '--force',
            action='store_true',
            help='Fuerza la recarga de datos, incluso si ya existen',
        )

    def handle(self, *args, **options):
        force = options['force']
        
        # Directorio donde están los fixtures
        fixtures_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), '..')
        
        # Lista de fixtures a cargar
        fixtures = [
            ('fixtures_mediums.json', Medium, 'mediums'),
            ('fixtures_channels.json', Channel, 'channels'),
            ('fixtures_action_types.json', ActionType, 'action types'),
            ('fixtures_actions.json', Action, 'actions'),
        ]
        
        for fixture_file, model_class, description in fixtures:
            fixture_path = os.path.join(fixtures_dir, fixture_file)
            
            if not os.path.exists(fixture_path):
                self.stdout.write(
                    self.style.WARNING(f'Fixture {fixture_file} no encontrado en {fixture_path}')
                )
                continue
            
            # Verificar si ya existen datos
            existing_count = model_class.objects.count()
            
            if existing_count > 0 and not force:
                self.stdout.write(
                    self.style.WARNING(
                        f'Ya existen {existing_count} {description}. '
                        f'Use --force para recargar los datos.'
                    )
                )
                continue
            
            # Cargar el fixture
            try:
                with open(fixture_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                if force and existing_count > 0:
                    # Eliminar datos existentes si se fuerza la recarga
                    model_class.objects.all().delete()
                    self.stdout.write(f'Eliminados {existing_count} {description} existentes')
                
                # Cargar usando loaddata
                call_command('loaddata', fixture_path, verbosity=0)
                
                new_count = model_class.objects.count()
                self.stdout.write(
                    self.style.SUCCESS(
                        f'✓ Cargados {new_count} {description} desde {fixture_file}'
                    )
                )
                
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'Error cargando {fixture_file}: {str(e)}')
                )
        
        self.stdout.write(
            self.style.SUCCESS('\n🎉 Carga de datos iniciales completada!')
        )
        
        # Mostrar resumen
        self.stdout.write('\n📊 Resumen de datos cargados:')
        self.stdout.write(f'  • Mediums: {Medium.objects.count()}')
        self.stdout.write(f'  • Channels: {Channel.objects.count()}')
        self.stdout.write(f'  • Action Types: {ActionType.objects.count()}')
        self.stdout.write(f'  • Actions: {Action.objects.count()}')
