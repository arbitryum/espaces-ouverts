from django.test import TestCase, override_settings
from django.urls import reverse


class HomeViewTests(TestCase):
    @override_settings(
        STORAGES={
            "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
            "staticfiles": {
                "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage"
            },
        }
    )
    def test_home_offers_both_products(self):
        response = self.client.get(reverse("home:index"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, reverse("spaces:index"))
        self.assertContains(response, reverse("coworking:home"))
