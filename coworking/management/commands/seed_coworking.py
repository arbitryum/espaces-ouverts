from django.core.management.base import BaseCommand

from coworking.models import CoworkingProject
from spaces.models import CareHome


PROJECTS = [
    {
        "name": "Atelier numérique intergénérationnel",
        "organization_name": "Les Liens du Canal",
        "description": "Une équipe associative anime des ateliers numériques ouverts aux habitants et aux résidents.",
        "location": "Paris 19e",
        "care_home": "EHPAD Les Jardins du Canal",
        "care_home_address": "12 avenue de Flandre, 75019 Paris",
        "status": "active",
        "is_published": True,
    },
    {
        "name": "Permanence d'accompagnement local",
        "organization_name": "Maison des Initiatives",
        "description": "Un collectif recherche un espace calme pour accueillir des permanences hebdomadaires de proximité.",
        "location": "Montreuil",
        "care_home": "Résidence Les Lilas",
        "care_home_address": "8 rue de Paris, 93100 Montreuil",
        "status": "seeking",
        "is_published": True,
    },
    {
        "name": "Projet à préparer",
        "organization_name": "Collectif Horizon",
        "description": "Ce projet est conservé comme exemple de brouillon et n'est pas encore visible publiquement.",
        "location": "Lyon",
        "care_home": "Maison de retraite Horizon",
        "care_home_address": "4 rue des Écoles, 69007 Lyon",
        "status": "draft",
        "is_published": False,
    },
]


class Command(BaseCommand):
    help = "Seed sample coworking projects for local development."

    def handle(self, *args, **options):
        created_count = 0
        updated_count = 0

        for project_data in PROJECTS:
            care_home, _ = CareHome.objects.get_or_create(
                name=project_data["care_home"],
                defaults={"address": project_data["care_home_address"]},
            )
            defaults = {
                key: value
                for key, value in project_data.items()
                if key not in {"name", "care_home", "care_home_address"}
            }
            project, created = CoworkingProject.objects.update_or_create(
                name=project_data["name"],
                defaults={**defaults, "care_home": care_home},
            )
            if created:
                created_count += 1
            else:
                updated_count += 1
            self.stdout.write(
                f"{'Created' if created else 'Updated'}: {project.name}"
            )

        self.stdout.write(
            self.style.SUCCESS(
                f"Seeded {created_count} coworking projects "
                f"({updated_count} updated, {CoworkingProject.objects.count()} total)."
            )
        )
