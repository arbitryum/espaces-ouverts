from datetime import time

from django.core.management.base import BaseCommand

from spaces.models import RecurringAvailability, Space


SCHEDULES = {
    "Le forum": [(1, "09:00", "17:00"), (3, "09:00", "17:00")],
    "Bibliothèque": [(0, "14:00", "18:00"), (4, "09:00", "12:00")],
    "Salle polyvalente": [(2, "10:00", "16:00")],
}


class Command(BaseCommand):
    help = "Seed recurring availability examples for existing spaces."

    def handle(self, *args, **options):
        created_count = 0
        for space_name, slots in SCHEDULES.items():
            spaces = Space.objects.filter(name=space_name)
            for space in spaces:
                for weekday, start, end in slots:
                    _, created = RecurringAvailability.objects.get_or_create(
                        space=space,
                        weekday=weekday,
                        start_time=time.fromisoformat(start),
                        end_time=time.fromisoformat(end),
                    )
                    if created:
                        created_count += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"Seeded {created_count} recurring availability slots."
            )
        )
