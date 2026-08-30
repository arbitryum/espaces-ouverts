from django.contrib.auth import get_user_model
from django.test import TestCase, override_settings
from django.urls import reverse

from .models import EhpadProfile


@override_settings(
    STORAGES={
        "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
        "staticfiles": {
            "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage"
        },
    }
)
class EhpadRegistrationTests(TestCase):
    def test_registration_form_has_password_controls_and_validation(self):
        response = self.client.get(reverse("accounts:register"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "password-validation.js")
        self.assertContains(response, "data-password-target=\"id_password1\"")
        self.assertContains(response, "data-password-rule=\"length\"")
        self.assertContains(response, "password-visible-icon")
        self.assertContains(response, "password-hidden-icon")

    def test_registration_creates_pending_inactive_profile(self):
        response = self.client.post(
            reverse("accounts:register"),
            {
                "username": "ehpad-contact",
                "email": "contact@example.org",
                "password1": "A-strong-password-123",
                "password2": "A-strong-password-123",
                "establishment_name": "EHPAD Les Tilleuls",
                "establishment_address": "1 rue des Tilleuls, Paris",
                "contact_name": "Marie Dupont",
                "modules": ["coworking"],
            },
        )

        self.assertRedirects(response, reverse("accounts:registration_pending"))
        user = get_user_model().objects.get(username="ehpad-contact")
        profile = user.ehpad_profile
        self.assertFalse(user.is_active)
        self.assertEqual(profile.status, EhpadProfile.STATUS_PENDING)
        self.assertFalse(profile.participates_in_spaces)
        self.assertTrue(profile.participates_in_coworking)

    def test_registration_requires_a_module(self):
        response = self.client.post(
            reverse("accounts:register"),
            {
                "username": "no-module",
                "email": "contact@example.org",
                "password1": "A-strong-password-123",
                "password2": "A-strong-password-123",
                "establishment_name": "EHPAD Les Tilleuls",
                "establishment_address": "1 rue des Tilleuls, Paris",
                "contact_name": "Marie Dupont",
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Sélectionnez au moins un dispositif.")
        self.assertFalse(get_user_model().objects.filter(username="no-module").exists())


class AccountLoginTemplateTests(TestCase):
    @override_settings(
        STORAGES={
            "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
            "staticfiles": {
                "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage"
            },
        }
    )
    def test_login_page_matches_password_control_design(self):
        response = self.client.get(reverse("accounts:login"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "password-validation.js")
        self.assertContains(response, 'data-password-target="id_password"')
        self.assertContains(response, "password-visible-icon")
        self.assertContains(response, reverse("accounts:register"))
        self.assertContains(response, 'class="input input-md w-full"')
        self.assertContains(response, 'class="mx-auto max-w-2xl"')
