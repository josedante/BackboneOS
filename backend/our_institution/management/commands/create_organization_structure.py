from django.core.management.base import BaseCommand
from django.db import transaction, IntegrityError
from our_institution.models import OurOrganization, Division, Seat, Unit, Position, Team
from world.models import Country, Industry, OrganizationType

class Command(BaseCommand):
    help = 'Crea datos completos de prueba para our_institution con estructura organizacional'

    def add_arguments(self, parser):
        parser.add_argument(
            '--reset',
            action='store_true',
            help='Elimina y recrea todos los datos de our_institution',
        )

    def handle(self, *args, **options):
        if options['reset']:
            self.stdout.write(self.style.WARNING('Eliminando datos existentes...'))
            with transaction.atomic():
                OurOrganization.objects.all().delete()
        
        if OurOrganization.objects.filter(is_active=True).exists():
            self.stdout.write(self.style.WARNING('Ya existe una organización activa. Use --reset para recrear.'))
            return

        try:
            with transaction.atomic():
                # Obtener o crear datos del mundo necesarios
                country, _ = Country.objects.get_or_create(
                    iso3_code='PER',
                    defaults={
                        'iso2_code': 'PE',
                        'name': 'Perú',
                        'official_name': 'República del Perú'
                    }
                )
                
                industry, _ = Industry.objects.get_or_create(
                    name='Tecnología de la Información',
                    defaults={'description': 'Desarrollo y consultoría en tecnología'}
                )
                
                org_type, _ = OrganizationType.objects.get_or_create(
                    name='SAC',
                    defaults={'description': 'Sociedad Anónima Cerrada'}
                )

                # Crear organización
                org = OurOrganization.objects.create(
                    name='BackboneOS',
                    legal_name='Backbone Operating Systems SAC',
                    tax_id='20500000000',
                    email='contacto@backboneos.com',
                    phone='+5111234567',
                    address='Av. Principal 123, Lima, Perú',
                    website='https://backboneos.com',
                    country=country,
                    industry=industry,
                    org_type=org_type,
                    is_active=True
                )
                self.stdout.write(self.style.SUCCESS(f'✓ Organización creada: {org.name}'))

                # Crear sedes
                sede_principal = Seat.objects.create(
                    name='Sede Principal',
                    code='HQ01',
                    category='HQT',
                    organization=org
                )
                
                sede_sucursal = Seat.objects.create(
                    name='Oficina Comercial',
                    code='COM01',
                    category='BRC',
                    organization=org
                )
                self.stdout.write(self.style.SUCCESS(f'✓ Sedes creadas: {sede_principal.name}, {sede_sucursal.name}'))

                # Crear divisiones
                divisiones_data = [
                    {'name': 'Tecnología y Desarrollo', 'code': 'TECH', 'desc': 'División especializada en desarrollo de software'},
                    {'name': 'Comercial y Marketing', 'code': 'COMM', 'desc': 'División de ventas y mercadeo'},
                    {'name': 'Operaciones y Finanzas', 'code': 'OPER', 'desc': 'División de operaciones y gestión financiera'},
                ]
                
                divisiones = {}
                for div_data in divisiones_data:
                    division = Division.objects.create(
                        name=div_data['name'],
                        code=div_data['code'],
                        description=div_data['desc'],
                        organization=org
                    )
                    divisiones[div_data['code']] = division
                    self.stdout.write(self.style.SUCCESS(f'  ✓ División: {division.name}'))

                # Crear estructura para División Tecnología
                tech_units_data = [
                    {'name': 'Gerencia de Desarrollo', 'code': 'GDEV', 'parent': None},
                    {'name': 'Equipo Frontend', 'code': 'FRONT', 'parent': 'GDEV'},
                    {'name': 'Equipo Backend', 'code': 'BACK', 'parent': 'GDEV'},
                    {'name': 'DevOps e Infraestructura', 'code': 'DEVOPS', 'parent': 'GDEV'},
                    {'name': 'QA y Testing', 'code': 'QA', 'parent': None},
                ]
                
                tech_units = {}
                for unit_data in tech_units_data:
                    parent = tech_units.get(unit_data['parent']) if unit_data['parent'] else None
                    unit = Unit.objects.create(
                        name=unit_data['name'],
                        code=unit_data['code'],
                        division=divisiones['TECH'],
                        parent=parent
                    )
                    tech_units[unit_data['code']] = unit
                    self.stdout.write(self.style.SUCCESS(f'    ✓ Unidad: {unit.name}'))

                # Crear posiciones para Tecnología
                positions_data = [
                    {'name': 'Gerente de Desarrollo', 'code': 'GER001', 'unit': 'GDEV'},
                    {'name': 'Tech Lead Frontend', 'code': 'TL001', 'unit': 'FRONT'},
                    {'name': 'Desarrollador Senior Frontend', 'code': 'DEV001', 'unit': 'FRONT'},
                    {'name': 'Desarrollador Junior Frontend', 'code': 'DEV002', 'unit': 'FRONT'},
                    {'name': 'Tech Lead Backend', 'code': 'TL002', 'unit': 'BACK'},
                    {'name': 'Desarrollador Senior Backend', 'code': 'DEV003', 'unit': 'BACK'},
                    {'name': 'Desarrollador Python', 'code': 'DEV004', 'unit': 'BACK'},
                    {'name': 'DevOps Engineer', 'code': 'DEVOPS001', 'unit': 'DEVOPS'},
                    {'name': 'QA Lead', 'code': 'QA001', 'unit': 'QA'},
                    {'name': 'QA Tester', 'code': 'QA002', 'unit': 'QA'},
                ]
                
                for pos_data in positions_data:
                    position = Position.objects.create(
                        name=pos_data['name'],
                        code=pos_data['code'],
                        unit=tech_units[pos_data['unit']]
                    )
                    self.stdout.write(self.style.SUCCESS(f'      ✓ Posición: {position.name}'))

                # Crear estructura para División Comercial
                comm_units_data = [
                    {'name': 'Gerencia Comercial', 'code': 'GCOM', 'parent': None},
                    {'name': 'Ventas Empresariales', 'code': 'VENT', 'parent': 'GCOM'},
                    {'name': 'Marketing Digital', 'code': 'MKTD', 'parent': 'GCOM'},
                ]
                
                comm_units = {}
                for unit_data in comm_units_data:
                    parent = comm_units.get(unit_data['parent']) if unit_data['parent'] else None
                    unit = Unit.objects.create(
                        name=unit_data['name'],
                        code=unit_data['code'],
                        division=divisiones['COMM'],
                        parent=parent
                    )
                    comm_units[unit_data['code']] = unit
                    self.stdout.write(self.style.SUCCESS(f'    ✓ Unidad: {unit.name}'))

                # Crear equipos
                teams_data = [
                    {'name': 'Squad CRM', 'code': 'CRM', 'division': 'TECH'},
                    {'name': 'Squad Analytics', 'code': 'ANALYTICS', 'division': 'TECH'},
                    {'name': 'Equipo Growth', 'code': 'GROWTH', 'division': 'COMM'},
                    {'name': 'Equipo Contenido', 'code': 'CONTENT', 'division': 'COMM'},
                ]
                
                for team_data in teams_data:
                    team = Team.objects.create(
                        name=team_data['name'],
                        code=team_data['code'],
                        division=divisiones[team_data['division']]
                    )
                    self.stdout.write(self.style.SUCCESS(f'    ✓ Equipo: {team.name}'))

                # Mostrar resumen
                self.stdout.write(self.style.SUCCESS('\n=== RESUMEN DE ESTRUCTURA ORGANIZACIONAL ==='))
                self.stdout.write(self.style.SUCCESS(f'Organización: {org.name}'))
                self.stdout.write(self.style.SUCCESS(f'Divisiones: {Division.objects.filter(organization=org).count()}'))
                self.stdout.write(self.style.SUCCESS(f'Sedes: {Seat.objects.filter(organization=org).count()}'))
                self.stdout.write(self.style.SUCCESS(f'Unidades: {Unit.objects.filter(division__organization=org).count()}'))
                self.stdout.write(self.style.SUCCESS(f'Posiciones: {Position.objects.filter(unit__division__organization=org).count()}'))
                self.stdout.write(self.style.SUCCESS(f'Equipos: {Team.objects.filter(division__organization=org).count()}'))
                
                self.stdout.write(self.style.SUCCESS('\n¡Estructura organizacional completa creada exitosamente!'))

        except IntegrityError as e:
            self.stderr.write(self.style.ERROR(f'Error de integridad: {e}'))
        except Exception as e:
            self.stderr.write(self.style.ERROR(f'Error inesperado: {e}'))
