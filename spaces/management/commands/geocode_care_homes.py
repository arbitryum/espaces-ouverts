from django.core.management.base import BaseCommand

from spaces.models import CareHome


class Command(BaseCommand):
    help = "Geocode care home addresses using the French BAN API."

    def add_arguments(self, parser):
        parser.add_argument(
            "--force",
            action="store_true",
            help="Re-geocode care homes even if they already have normalized address details.",
        )

    def handle(self, *args, **options):
        force = options["force"]
        queryset = CareHome.objects.all().order_by("name")
        if not force:
            queryset = queryset.filter(address_details__isnull=True)

        total = queryset.count()
        self.stdout.write(f"Geocoding {total} care homes...")

        success_count = 0
        not_found_count = 0
        failure_count = 0

        for care_home in queryset:
            try:
                result = care_home.refresh_address_details_from_ban(save=True)
            except RuntimeError as exc:
                failure_count += 1
                self.stdout.write(
                    self.style.WARNING(f"  ✗ {care_home.name}: {exc}")
                )
                continue

            if result is None:
                not_found_count += 1
                self.stdout.write(
                    self.style.WARNING(f"  ? {care_home.name}: no BAN match")
                )
                continue

            success_count += 1
            self.stdout.write(
                self.style.SUCCESS(
                    f"  ✓ {care_home.name}: {result.city} ({result.department_code}) [{result.latitude}, {result.longitude}]"
                )
            )

        self.stdout.write(
            self.style.SUCCESS(
                f"Done. success={success_count} not_found={not_found_count} failed={failure_count}"
            )
        )
