from django.test import TestCase, override_settings
from django.urls import reverse


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
