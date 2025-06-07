from django.core.management.base import BaseCommand
from our_institution.models import OurOrganization
from django.db import IntegrityError

class Command(BaseCommand):
    help = 'Inicializa la organización propietaria del sistema si no existe'

    def handle(self, *args, **options):
        if OurOrganization.objects.filter(is_active=True).exists():
            self.stdout.write(self.style.WARNING('Ya existe una organización activa.'))
            return

        try:
            org = OurOrganization.objects.create(
                name='BackboneOS',
                legal_name='Backbone Operating Systems SAC',
                tax_id='20500000000',
                email='contacto@backboneos.com',
                phone='+5111234567',
                address='Av. Principal 123, Lima',
                website='https://backboneos.com',
                is_active=True
            )
            self.stdout.write(self.style.SUCCESS(f'Organización creada: {org.name}'))
        except IntegrityError as e:
            self.stderr.write(self.style.ERROR(f'Error de integridad: {e}'))
