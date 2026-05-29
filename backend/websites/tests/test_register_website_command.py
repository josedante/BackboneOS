import json
import tempfile
import os

from django.core.management import call_command
from django.core.management.base import CommandError
from django.test import TestCase

from our_institution.models import Division, OurOrganization
from websites.models import Website


class RegisterWebsiteCommandTests(TestCase):
    def test_bootstraps_full_chain_on_empty_db(self):
        call_command("register_website", url="https://example.com")
        org = OurOrganization.objects.get()
        self.assertEqual(org.name, "Default Organization")
        self.assertTrue(org.is_active)
        division = Division.objects.get()
        self.assertEqual(division.organization, org)
        website = Website.objects.get(base_url="https://example.com")
        self.assertTrue(website.active)
        self.assertEqual(website.division, division)
        self.assertIsNotNone(website.channel)

    def test_reuses_existing_active_organization(self):
        acme = OurOrganization.objects.create(name="Acme Inc", is_active=True)
        call_command("register_website", url="https://example.com")
        self.assertEqual(OurOrganization.objects.count(), 1)
        self.assertEqual(
            Website.objects.get(base_url="https://example.com").division.organization, acme)

    def test_explicit_organization_falls_back_to_active_org(self):
        acme = OurOrganization.objects.create(name="Acme Inc", is_active=True)
        call_command("register_website", url="https://example.com", organization="Other Org")
        # Falls back to the existing active org; no second org created, no error.
        self.assertEqual(OurOrganization.objects.count(), 1)
        self.assertFalse(OurOrganization.objects.filter(name="Other Org").exists())
        self.assertEqual(
            Website.objects.get(base_url="https://example.com").division.organization, acme)

    def test_idempotent_rerun(self):
        call_command("register_website", url="https://example.com")
        call_command("register_website", url="https://example.com")
        self.assertEqual(OurOrganization.objects.count(), 1)
        self.assertEqual(Division.objects.count(), 1)
        self.assertEqual(Website.objects.filter(base_url="https://example.com").count(), 1)

    def test_dry_run_writes_nothing(self):
        call_command("register_website", url="https://example.com", dry_run=True)
        self.assertEqual(OurOrganization.objects.count(), 0)
        self.assertEqual(Division.objects.count(), 0)
        self.assertEqual(Website.objects.count(), 0)

    def test_reactivates_inactive_website(self):
        org = OurOrganization.objects.create(name="Acme Inc", is_active=True)
        division = Division.objects.create(organization=org, name="Marketing",
                                           code="MKT", is_active=True)
        website = Website.objects.create(name="Example", base_url="https://example.com",
                                         division=division, active=False)
        call_command("register_website", url="https://example.com")
        website.refresh_from_db()
        self.assertTrue(website.active)
        self.assertEqual(Website.objects.filter(base_url="https://example.com").count(), 1)

    def test_from_file_bulk_registration(self):
        payload = [
            {"base_url": "https://example.com", "name": "Example", "division": "Marketing"},
            {"base_url": "https://blog.example.com"},
        ]
        fd, path = tempfile.mkstemp(suffix=".json")
        try:
            with os.fdopen(fd, "w", encoding="utf-8") as handle:
                json.dump(payload, handle)
            call_command("register_website", from_file=path)
        finally:
            os.remove(path)
        self.assertTrue(Website.objects.filter(base_url="https://example.com").exists())
        self.assertTrue(Website.objects.filter(base_url="https://blog.example.com").exists())
        self.assertTrue(Division.objects.filter(name="Default Division").exists())
        self.assertTrue(Division.objects.filter(name="Marketing").exists())

    def test_requires_url_or_from_file(self):
        with self.assertRaises(CommandError):
            call_command("register_website")
