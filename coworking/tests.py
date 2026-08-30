from django.core.management import call_command
from django.test import TestCase, override_settings
from django.urls import reverse
from django.utils import timezone

from .models import CoworkingProject
from spaces.models import CareHome, Space
from .management.commands.seed_coworking import PROJECTS


class CoworkingHomeViewTests(TestCase):
    @override_settings(
        STORAGES={
            "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
            "staticfiles": {
                "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage"
            },
        }
    )
    def test_home_button_links_to_visitor_home(self):
        response = self.client.get(reverse("coworking:home"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'href="/"')


@override_settings(
    STORAGES={
        "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
        "staticfiles": {
            "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage"
        },
    }
)
class CoworkingProjectDirectoryTests(TestCase):
    def test_seed_command_does_not_delete_spaces(self):
        care_home = CareHome.objects.create(
            name="Espace Ouvert existant",
            address="1 rue de Paris",
        )
        Space.objects.create(
            care_home=care_home,
            name="Salle existante",
            pub_date=timezone.now(),
        )

        call_command("seed_coworking")

        self.assertEqual(Space.objects.count(), 1)

    def test_seed_data_has_published_and_draft_examples(self):
        self.assertEqual(len(PROJECTS), 3)
        self.assertEqual(sum(project["is_published"] for project in PROJECTS), 2)

    def test_directory_only_lists_published_projects(self):
        CoworkingProject.objects.create(
            name="Projet publié",
            organization_name="Collectif local",
            description="Un projet de proximité.",
            location="Paris",
            status="seeking",
            is_published=True,
        )
        CoworkingProject.objects.create(
            name="Projet brouillon",
            organization_name="Collectif local",
            description="Ne doit pas apparaître.",
            location="Lyon",
            status="draft",
            is_published=False,
        )

        response = self.client.get(reverse("coworking:project_list"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Projet publié")
        self.assertNotContains(response, "Projet brouillon")
