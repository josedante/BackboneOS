"""
Register owned websites for BackboneOS tracking.

This command bootstraps the full prerequisite chain so it works on an empty
database:

    OurOrganization  ->  Division  ->  Website  ->  Channel (auto on save)

It is idempotent: existing organizations, divisions and websites are reused,
and a website that was previously soft-deleted (active=False) is reactivated.
"""

import json
from urllib.parse import urlparse

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from our_institution.models import Division, OurOrganization
from websites.models import Website

DEFAULT_ORGANIZATION_NAME = "Default Organization"
DEFAULT_DIVISION_NAME = "Default Division"


class Command(BaseCommand):
    help = (
        "Register owned websites for tracking, creating any missing prerequisite "
        "organization and division along the way."
    )

    def add_arguments(self, parser):
        parser.add_argument("--url", metavar="BASE_URL",
                            help="Base URL to register (required unless --from-file)")
        parser.add_argument("--name", help="Display name (defaults to the domain)")
        parser.add_argument("--organization",
                            help="Organization name; defaults to the active org, "
                                 "or a new one if none exists")
        parser.add_argument("--division", default=DEFAULT_DIVISION_NAME,
                            help=f'Division name (default: "{DEFAULT_DIVISION_NAME}")')
        parser.add_argument("--division-code", dest="division_code",
                            help="Division code (defaults to the initials of the name)")
        parser.add_argument("--from-file", dest="from_file", metavar="PATH",
                            help="JSON file with a list of websites to register")
        parser.add_argument("--dry-run", action="store_true",
                            help="Show actions without writing anything")

    def handle(self, *args, **options):
        dry_run = options["dry_run"]

        if not options.get("url") and not options.get("from_file"):
            raise CommandError("Provide --url or --from-file.")

        sites = self._load_sites(options)
        if not sites:
            raise CommandError("No websites to register.")

        if dry_run:
            self._register_all(sites, options, dry_run=True)
            self.stdout.write(self.style.WARNING("\nDry run - no changes were made."))
        else:
            with transaction.atomic():
                self._register_all(sites, options, dry_run=False)
            self.stdout.write(self.style.SUCCESS("\nDone."))

    def _register_all(self, sites, options, dry_run):
        organization = self._resolve_organization(options.get("organization"), dry_run)
        division_cache = {}
        for site in sites:
            self.stdout.write(f"\n-> {site['base_url']}")
            self._process_site(site, organization, division_cache, options, dry_run)

    # Organization (respects the single-active-instance invariant) -----------

    def _resolve_organization(self, name, dry_run):
        active = OurOrganization.objects.filter(is_active=True).first()
        if name:
            if active and active.name != name:
                # Respect the single-active-org invariant: fall back silently.
                self.stdout.write(
                    f'Using active organization: "{active}" '
                    f'(ignoring --organization "{name}")'
                )
                return active
            return self._get_or_create_organization(name, dry_run)
        if active:
            self.stdout.write(f'Using active organization: "{active}"')
            return active
        return self._get_or_create_organization(DEFAULT_ORGANIZATION_NAME, dry_run)

    def _get_or_create_organization(self, name, dry_run):
        existing = OurOrganization.objects.filter(name=name).first()
        if existing:
            self.stdout.write(f'Using organization: "{existing}"')
            return existing
        if dry_run:
            self.stdout.write(self.style.WARNING(f'Would create organization: "{name}"'))
            return None
        organization = OurOrganization.objects.create(name=name, is_active=True)
        self.stdout.write(self.style.SUCCESS(f'Created organization: "{organization}"'))
        return organization

    # Division ----------------------------------------------------------------

    def _ensure_division(self, organization, name, code, cache, dry_run):
        cache_key = (organization.pk if organization else None, name)
        if cache_key in cache:
            return cache[cache_key]

        division = None
        if organization is not None:
            division = Division.objects.filter(organization=organization, name=name).first()

        if division:
            self.stdout.write(f'    Division already exists: "{name}"')
        elif dry_run:
            self.stdout.write(self.style.WARNING(f'    Would create Division: "{name}" (code={code})'))
            division = None
        else:
            division = Division.objects.create(
                organization=organization, name=name, code=code,
                description=f"{name} division", is_active=True,
            )
            self.stdout.write(self.style.SUCCESS(f'    Created Division: "{name}" (code={code})'))

        cache[cache_key] = division
        return division

    # Website -----------------------------------------------------------------

    def _process_site(self, site, organization, division_cache, options, dry_run):
        base_url = site["base_url"]
        name = site.get("name") or self._domain(base_url)
        division_name = site.get("division") or options["division"]
        division_code = options.get("division_code") or self._derive_code(division_name)

        division = self._ensure_division(organization, division_name, division_code,
                                         division_cache, dry_run)

        existing = Website.objects.filter(base_url=base_url).first()
        if existing:
            if existing.active:
                self.stdout.write(self.style.SUCCESS(f"    Already registered and active: {base_url}"))
            elif dry_run:
                self.stdout.write(self.style.WARNING(f"    Would reactivate Website: {base_url}"))
            else:
                existing.active = True
                existing.save(update_fields=["active"])
                self.stdout.write(self.style.SUCCESS(f"    Reactivated Website: {base_url}"))
            return

        if dry_run:
            self.stdout.write(self.style.WARNING(
                f'    Would create Website: {base_url} (name="{name}", division="{division_name}")'))
            return

        if division is None:
            raise CommandError(f"Cannot create {base_url}: division could not be resolved.")

        # Website.save() creates the associated tracking Channel automatically.
        website = Website.objects.create(name=name, base_url=base_url,
                                         division=division, active=True)
        self.stdout.write(self.style.SUCCESS(
            f"    Created Website: {website} (channel: {website.channel})"))

    # Input loading and helpers ----------------------------------------------

    def _load_sites(self, options):
        sites = []
        from_file = options.get("from_file")
        if from_file:
            try:
                with open(from_file, "r", encoding="utf-8") as handle:
                    data = json.load(handle)
            except (OSError, json.JSONDecodeError) as exc:
                raise CommandError(f"Could not read --from-file {from_file!r}: {exc}")
            if not isinstance(data, list):
                raise CommandError("--from-file must contain a JSON list of website objects.")
            for index, entry in enumerate(data):
                if not isinstance(entry, dict) or not entry.get("base_url"):
                    raise CommandError(
                        f"Entry {index} in --from-file is missing the required 'base_url' field.")
                sites.append(entry)
        if options.get("url"):
            sites.append({"base_url": options["url"], "name": options.get("name"),
                          "division": options.get("division")})
        return sites

    @staticmethod
    def _domain(url):
        parsed = urlparse(url)
        domain = parsed.netloc or parsed.path
        return domain.replace("www.", "") or url

    @staticmethod
    def _derive_code(name):
        code = "".join(word[0] for word in name.split() if word).upper()[:20]
        return code or "DEFAULT"
