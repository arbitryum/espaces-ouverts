import datetime
from unittest.mock import patch

from django.test import TestCase, override_settings
from django.urls import reverse
from django.utils import timezone

from spaces.models import Address, CareHome, RecurringAvailability, Space
from spaces.management.commands.seed_availability import SCHEDULES


class SpaceModelTests(TestCase):
    def test_publication_status_controls_public_visibility(self):
        draft = Space(publication_status="draft", pub_date=timezone.now())

        self.assertFalse(draft.is_public())

    def test_recurring_availability_is_ordered_by_weekday_and_start_time(self):
        space = create_space(name="Weekly space", days=-1)
        late = RecurringAvailability.objects.create(
            space=space,
            weekday=2,
            start_time="14:00",
            end_time="16:00",
        )
        early = RecurringAvailability.objects.create(
            space=space,
            weekday=1,
            start_time="09:00",
            end_time="11:00",
        )

        self.assertEqual(list(space.recurring_availability.all()), [early, late])

    @override_settings(
        STORAGES={
            "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
            "staticfiles": {
                "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage"
            },
        }
    )
    def test_detail_displays_recurring_availability(self):
        space = create_space(name="Calendar space", days=-1)
        RecurringAvailability.objects.create(
            space=space,
            weekday=0,
            start_time="09:30",
            end_time="12:00",
        )

        response = self.client.get(reverse("spaces:detail", args=[space.pk]))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Lundi")
        self.assertContains(response, "09:30")

    def test_availability_seed_defines_examples(self):
        self.assertIn("Le forum", SCHEDULES)
        self.assertTrue(SCHEDULES["Le forum"])

    def test_was_published_recently_with_future_space(self):
        """
        was_published_recently() returns False for spaces whose pub_date
        is in the future.
        """
        time = timezone.now() + datetime.timedelta(days=30)
        future_space = Space(pub_date=time)
        self.assertIs(future_space.was_published_recently(), False)

    def test_was_published_recently_with_old_space(self):
        """
        was_published_recently() returns False for spaces whose pub_date
        is older than 1 day.
        """
        time = timezone.now() - datetime.timedelta(days=1, seconds=1)
        old_space = Space(pub_date=time)
        self.assertIs(old_space.was_published_recently(), False)

    def test_was_published_recently_with_recent_space(self):
        """
        was_published_recently() returns True for spaces whose pub_date
        is within the last day.
        """
        time = timezone.now() - datetime.timedelta(hours=23, minutes=59, seconds=59)
        recent_space = Space(pub_date=time)
        self.assertIs(recent_space.was_published_recently(), True)

    def test_address_osm_embed_data_is_focused(self):
        address = Address(
            raw_address="9 Rue Maria Helena Vieira da Silva, 75014 Paris",
            latitude=48.8301,
            longitude=2.3202,
        )

        self.assertTrue(address.has_coordinates)
        self.assertEqual(address.osm_bbox, "2.310200,48.820100,2.330200,48.840100")
        self.assertIn("bbox=2.310200,48.820100,2.330200,48.840100", address.osm_embed_url)


def create_care_home(name, address):
    """
    Create a care home with the given `name` and `address`.
    """
    return CareHome.objects.create(name=name, address=address)

def create_space(
    name,
    days,
    care_home_name="Test Care Home",
    care_home_address="123 Test St",
):
    """
    Create a space with the given `name` and published the
    given number of `days` offset to now (negative for spaces published
    in the past, positive for spaces that have yet to be published).
    """
    time = timezone.now() + datetime.timedelta(days=days)
    care_home = create_care_home(name=care_home_name, address=care_home_address)
    return Space.objects.create(name=name, pub_date=time, care_home=care_home)

class SpaceIndexViewTests(TestCase):
    @override_settings(
        STORAGES={
            "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
            "staticfiles": {
                "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage"
            },
        }
    )
    def test_home_button_links_to_visitor_home(self):
        response = self.client.get(reverse("spaces:index"))

        self.assertContains(response, 'href="/"')

    def test_default_view_mode_is_list(self):
        create_space(name="Past space.", days=-1)

        response = self.client.get(reverse("spaces:index"))

        self.assertEqual(response.context["view_mode"], "list")

    def test_map_view_mode_includes_markers(self):
        address = Address.objects.create(
            raw_address="9 Rue Maria Helena Vieira da Silva, 75014 Paris",
            label="9 Rue Maria Helena Vieira da Silva 75014 Paris",
            city="Paris",
            postal_code="75014",
            department_code="75",
            department_name="Paris",
            region_name="Île-de-France",
            latitude=48.8301,
            longitude=2.3202,
        )
        care_home = create_care_home(name="Maison Carte", address="Adresse carte")
        care_home.address_details = address
        care_home.save(update_fields=["address_details"])
        Space.objects.create(
            care_home=care_home,
            name="Space map",
            availability="Disponible",
            pub_date=timezone.now() - datetime.timedelta(days=1),
            description="Test",
        )

        response = self.client.get(reverse("spaces:index"), {"view_mode": "map"})

        self.assertEqual(response.context["view_mode"], "map")
        self.assertEqual(response.context["map_markers_count"], 1)

    def test_no_spaces(self):
        """
        If no spaces exist, an appropriate message is displayed.
        """
        response = self.client.get(reverse("spaces:index"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No spaces are available.")
        self.assertQuerySetEqual(response.context["space_list"], [])

    def test_past_space(self):
        """
        Spaces with a pub_date in the past are displayed on the
        index page.
        """
        space = create_space(name="Past space.", days=-30)
        response = self.client.get(reverse("spaces:index"))
        self.assertQuerySetEqual(
            response.context["space_list"],
            [space],
        )

    def test_future_space(self):
        """
        Spaces with a pub_date in the future aren't displayed on
        the index page.
        """
        create_space(name="Future space.", days=30)
        response = self.client.get(reverse("spaces:index"))
        self.assertContains(response, "No spaces are available.")
        self.assertQuerySetEqual(response.context["space_list"], [])

    def test_future_space_and_past_space(self):
        """
        Even if both past and future spaces exist, only past spaces
        are displayed.
        """
        space = create_space(name="Past space.", days=-30)
        create_space(name="Future space.", days=30)
        response = self.client.get(reverse("spaces:index"))
        self.assertQuerySetEqual(
            response.context["space_list"],
            [space],
        )

    def test_two_past_spaces(self):
        """
        The spaces index page may display multiple spaces.
        """
        space1 = create_space(name="Past space 1.", days=-30)
        space2 = create_space(name="Past space 2.", days=-5)
        response = self.client.get(reverse("spaces:index"))
        self.assertQuerySetEqual(
            response.context["space_list"],
            [space2, space1],
        )

    def test_filter_by_location_in_care_home_address(self):
        paris_space = create_space(
            name="Paris space.",
            days=-1,
            care_home_name="Maison Paris",
            care_home_address="10 rue de Rivoli, Paris, France",
        )
        create_space(
            name="Lyon space.",
            days=-1,
            care_home_name="Maison Lyon",
            care_home_address="20 place Bellecour, Lyon, France",
        )

        response = self.client.get(reverse("spaces:index"), {"location": "Paris"})

        self.assertQuerySetEqual(response.context["space_list"], [paris_space])

    @patch("spaces.views.resolve_location_query_with_ban")
    def test_filter_by_location_uses_local_match_without_ban_lookup(self, mocked_ban_resolver):
        paris_space = create_space(
            name="Paris local space.",
            days=-1,
            care_home_name="Maison Locale",
            care_home_address="10 rue de Rivoli, Paris, France",
        )

        response = self.client.get(reverse("spaces:index"), {"location": "Paris"})

        self.assertQuerySetEqual(response.context["space_list"], [paris_space])
        mocked_ban_resolver.assert_not_called()

    def test_filter_by_department_code_in_care_home_address(self):
        dep_75_space = create_space(
            name="Dep 75 space.",
            days=-1,
            care_home_name="Maison 75",
            care_home_address="75011 Paris, France",
        )
        create_space(
            name="Dep 69 space.",
            days=-1,
            care_home_name="Maison 69",
            care_home_address="69002 Lyon, France",
        )

        response = self.client.get(reverse("spaces:index"), {"location": "75"})

        self.assertQuerySetEqual(response.context["space_list"], [dep_75_space])

    def test_filter_by_location_in_normalized_city(self):
        normalized_address = Address.objects.create(
            raw_address="Adresse normalisée 1",
            label="10 rue de Rivoli 75001 Paris",
            city="Paris",
            postal_code="75001",
            department_code="75",
            department_name="Paris",
            latitude=48.8557,
            longitude=2.3590,
        )
        care_home = create_care_home(name="Maison Normalisée", address="Adresse brute")
        care_home.address_details = normalized_address
        care_home.save(update_fields=["address_details"])
        matching_space = Space.objects.create(
            care_home=care_home,
            name="Normalized city space",
            availability="Disponible",
            pub_date=timezone.now() - datetime.timedelta(days=1),
            description="Test",
        )

        response = self.client.get(reverse("spaces:index"), {"location": "Paris"})

        self.assertQuerySetEqual(response.context["space_list"], [matching_space])

    def test_filter_by_location_in_normalized_department(self):
        normalized_address = Address.objects.create(
            raw_address="Adresse normalisée 2",
            label="20 avenue de la République 59000 Lille",
            city="Lille",
            postal_code="59000",
            department_code="59",
            department_name="Nord",
            latitude=50.6292,
            longitude=3.0573,
        )
        care_home = create_care_home(name="Maison Nord", address="Adresse brute nord")
        care_home.address_details = normalized_address
        care_home.save(update_fields=["address_details"])
        matching_space = Space.objects.create(
            care_home=care_home,
            name="Normalized department space",
            availability="Disponible",
            pub_date=timezone.now() - datetime.timedelta(days=1),
            description="Test",
        )

        response = self.client.get(reverse("spaces:index"), {"location": "59"})

        self.assertQuerySetEqual(response.context["space_list"], [matching_space])

    def test_filter_by_location_in_normalized_department_name(self):
        normalized_address = Address.objects.create(
            raw_address="Adresse normalisée 3",
            label="20 avenue de la République 59000 Lille",
            city="Lille",
            postal_code="59000",
            department_code="59",
            department_name="Nord",
            latitude=50.6292,
            longitude=3.0573,
        )
        care_home = create_care_home(name="Maison Nord", address="Adresse brute nord")
        care_home.address_details = normalized_address
        care_home.save(update_fields=["address_details"])
        matching_space = Space.objects.create(
            care_home=care_home,
            name="Normalized department name space",
            availability="Disponible",
            pub_date=timezone.now() - datetime.timedelta(days=1),
            description="Test",
        )

        response = self.client.get(reverse("spaces:index"), {"location": "Nord"})

        self.assertQuerySetEqual(response.context["space_list"], [matching_space])

    def test_filter_by_location_in_normalized_region_name(self):
        normalized_address = Address.objects.create(
            raw_address="Adresse normalisée 4",
            label="9 Rue Maria Helena Vieira da Silva 75014 Paris",
            city="Paris",
            postal_code="75014",
            department_code="75",
            department_name="Paris",
            region_name="Île-de-France",
            latitude=48.8301,
            longitude=2.3202,
        )
        care_home = create_care_home(name="Maison IDF", address="Adresse brute idf")
        care_home.address_details = normalized_address
        care_home.save(update_fields=["address_details"])
        matching_space = Space.objects.create(
            care_home=care_home,
            name="Normalized region space",
            availability="Disponible",
            pub_date=timezone.now() - datetime.timedelta(days=1),
            description="Test",
        )

        response = self.client.get(reverse("spaces:index"), {"location": "ile de france"})

        self.assertQuerySetEqual(response.context["space_list"], [matching_space])

    @patch("spaces.views.resolve_location_query_with_ban")
    def test_filter_by_location_uses_ban_resolved_terms(self, mocked_ban_resolver):
        mocked_ban_resolver.return_value = {
            "terms": ["Île-de-France", "Paris", "75"],
        }
        normalized_address = Address.objects.create(
            raw_address="Adresse normalisée 5",
            label="Lieu en région Île-de-France",
            city="Paris",
            postal_code="75014",
            department_code="75",
            department_name="Paris",
            region_name="Île-de-France",
            latitude=48.8301,
            longitude=2.3202,
        )
        care_home = create_care_home(name="Maison API", address="Adresse brute API")
        care_home.address_details = normalized_address
        care_home.save(update_fields=["address_details"])
        matching_space = Space.objects.create(
            care_home=care_home,
            name="BAN resolved space",
            availability="Disponible",
            pub_date=timezone.now() - datetime.timedelta(days=1),
            description="Test",
        )

        response = self.client.get(reverse("spaces:index"), {"location": "idf"})

        self.assertQuerySetEqual(response.context["space_list"], [matching_space])
        mocked_ban_resolver.assert_called_once_with("idf")

    def test_filter_around_me_with_radius(self):
        nearby_address = Address.objects.create(
            raw_address="Adresse proche",
            label="Paris centre",
            city="Paris",
            postal_code="75001",
            department_code="75",
            department_name="Paris",
            region_name="Île-de-France",
            latitude=48.8566,
            longitude=2.3522,
        )
        far_address = Address.objects.create(
            raw_address="Adresse lointaine",
            label="Lyon centre",
            city="Lyon",
            postal_code="69001",
            department_code="69",
            department_name="Rhône",
            region_name="Auvergne-Rhône-Alpes",
            latitude=45.7640,
            longitude=4.8357,
        )

        nearby_home = create_care_home(name="Maison Proche", address="Paris")
        nearby_home.address_details = nearby_address
        nearby_home.save(update_fields=["address_details"])
        nearby_space = Space.objects.create(
            care_home=nearby_home,
            name="Space proche",
            availability="Disponible",
            pub_date=timezone.now() - datetime.timedelta(days=1),
            description="Test",
        )

        far_home = create_care_home(name="Maison Lointaine", address="Lyon")
        far_home.address_details = far_address
        far_home.save(update_fields=["address_details"])
        Space.objects.create(
            care_home=far_home,
            name="Space loin",
            availability="Disponible",
            pub_date=timezone.now() - datetime.timedelta(days=1),
            description="Test",
        )

        response = self.client.get(
            reverse("spaces:index"),
            {
                "near_lat": "48.8566",
                "near_lon": "2.3522",
                "radius_km": "5",
                "near_mode": "around_me",
            },
        )

        self.assertEqual(list(response.context["space_list"]), [nearby_space])
        self.assertTrue(response.context["around_me_active"])
        self.assertEqual(response.context["around_me_radius_km"], "5")
        self.assertAlmostEqual(response.context["space_list"][0].distance_km, 0.0, places=4)


class CareHomeAddressNormalizationTests(TestCase):
    @patch("spaces.services.geocoding.geocode_address_with_ban")
    def test_refresh_address_details_from_ban_creates_normalized_address(self, mocked_geocoder):
        mocked_geocoder.return_value = {
            "label": "9 Rue Maria Helena Vieira da Silva 75014 Paris",
            "city": "Paris",
            "postal_code": "75014",
            "city_code": "75114",
            "department_code": "75",
            "department_name": "Paris",
            "region_name": "Île-de-France",
            "latitude": 48.8301,
            "longitude": 2.3202,
            "ban_id": "75114_0009",
            "ban_score": 0.97,
        }
        care_home = create_care_home(
            name="Alice Prin",
            address="9 Rue Maria Helena Vieira da Silva, 75014 Paris",
        )

        result = care_home.refresh_address_details_from_ban(save=True)

        self.assertIsNotNone(result)
        care_home.refresh_from_db()
        self.assertIsNotNone(care_home.address_details)
        self.assertEqual(care_home.address_details.city, "Paris")
        self.assertEqual(care_home.address_details.department_code, "75")
        self.assertEqual(care_home.address_details.latitude, 48.8301)
        mocked_geocoder.assert_called_once_with("9 Rue Maria Helena Vieira da Silva, 75014 Paris")

class SpaceDetailViewTests(TestCase):
    def test_future_space(self):
        """
        The detail view of a space with a pub_date in the future
        returns a 404 not found.
        """
        future_space = create_space(name="Future space.", days=5)
        url = reverse("spaces:detail", args=(future_space.id,))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_past_space(self):
        """
        The detail view of a space with a pub_date in the past
        displays the space's name.
        """
        past_space = create_space(name="Past Space.", days=-5)
        url = reverse("spaces:detail", args=(past_space.id,))
        response = self.client.get(url)
        self.assertContains(response, past_space.name)


class LocationSuggestionViewTests(TestCase):
    @patch("spaces.views.search_locations_with_ban")
    def test_location_suggestions_returns_ban_results(self, mocked_search):
        mocked_search.return_value = [
            {
                "label": "Paris (75000)",
                "name": "Paris",
                "city": "Paris",
                "postcode": "75000",
                "type": "municipality",
                "department_code": "75",
                "department_name": "Paris",
                "region_name": "Île-de-France",
                "latitude": 48.8566,
                "longitude": 2.3522,
            }
        ]

        response = self.client.get(reverse("spaces:location_suggestions"), {"q": "par"})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["results"][0]["label"], "Paris (75000)")
        mocked_search.assert_called_once_with("par")

    @patch("spaces.views.search_locations_with_ban")
    def test_location_suggestions_short_query_returns_empty(self, mocked_search):
        response = self.client.get(reverse("spaces:location_suggestions"), {"q": "p"})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["results"], [])
        mocked_search.assert_not_called()
