from django.test import TestCase
from .models import OurOrganization, Seat, Unit, Position, Team

class OurOrganizationModelTest(TestCase):
    def test_unique_active_constraint(self):
        org1 = OurOrganization.objects.create(name='Org 1', is_active=True)
        with self.assertRaises(Exception):
            OurOrganization.objects.create(name='Org 2', is_active=True)

class SeatModelTest(TestCase):
    def test_creation(self):
        org = OurOrganization.objects.create(name='Org X', is_active=True)
        seat = Seat.objects.create(name='Sede Central', code='HQT1', organization=org)
        self.assertEqual(seat.organization, org)

class UnitModelTest(TestCase):
    def test_hierarchy(self):
        parent = Unit.objects.create(name='Gerencia')
        child = Unit.objects.create(name='Marketing', parent=parent)
        self.assertEqual(child.parent, parent)

class PositionModelTest(TestCase):
    def test_link_to_unit(self):
        unit = Unit.objects.create(name='TI')
        position = Position.objects.create(title='DevOps', unit=unit)
        self.assertEqual(position.unit, unit)

class TeamModelTest(TestCase):
    def test_creation(self):
        team = Team.objects.create(name='Innovación')
        self.assertTrue(team.is_active)
