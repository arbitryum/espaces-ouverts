from math import asin, cos, radians, sin, sqrt

from django.contrib import messages
from django.db.models import Q
from django.http import Http404, HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, render
from django.template import loader
from django.urls import reverse
from django.utils import timezone
from django.views import generic

from spaces.models import CareHome, Space, normalize_for_search
from spaces.services.geocoding import (resolve_location_query_with_ban,
                                       search_locations_with_ban)


class IndexView(generic.ListView):
    template_name = "spaces/index.html"
    context_object_name = "space_list"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.around_me_active = False
        self.around_me_radius_km = ""

    @staticmethod
    def _parse_float(value):
        try:
            return float(value)
        except (TypeError, ValueError):
            return None

    @staticmethod
    def _distance_km(lat1, lon1, lat2, lon2):
        earth_radius_km = 6371.0
        lat1_rad = radians(lat1)
        lon1_rad = radians(lon1)
        lat2_rad = radians(lat2)
        lon2_rad = radians(lon2)
        delta_lat = lat2_rad - lat1_rad
        delta_lon = lon2_rad - lon1_rad
        a = sin(delta_lat / 2) ** 2 + cos(lat1_rad) * cos(lat2_rad) * sin(delta_lon / 2) ** 2
        c = 2 * asin(sqrt(a))
        return earth_radius_km * c

    def _filter_around_me(self, queryset):
        near_lat = self._parse_float(self.request.GET.get("near_lat", "").strip())
        near_lon = self._parse_float(self.request.GET.get("near_lon", "").strip())
        near_mode = self.request.GET.get("near_mode", "").strip()
        radius_km = self._parse_float(self.request.GET.get("radius_km", "").strip() or "20")

        if near_lat is None or near_lon is None:
            return queryset

        if radius_km is None or radius_km <= 0:
            messages.warning(self.request, "Rayon invalide pour la recherche autour de moi.")
            return queryset

        self.around_me_active = near_mode == "around_me"
        if self.around_me_active:
            self.around_me_radius_km = f"{radius_km:g}"
        matching_spaces = []
        for space in queryset:
            address_details = space.care_home.address_details
            if not address_details or not address_details.has_coordinates:
                continue
            distance_km = self._distance_km(
                near_lat,
                near_lon,
                address_details.latitude,
                address_details.longitude,
            )
            if distance_km <= radius_km:
                space.distance_km = distance_km
                matching_spaces.append(space)

        if not matching_spaces:
            return []

        matching_spaces.sort(key=lambda current_space: current_space.distance_km)
        return matching_spaces

    def get_queryset(self):
        """Return published spaces, optionally filtered by location and care home."""
        queryset = (
            Space.objects.filter(pub_date__lte=timezone.now(), status="available")
            .select_related("care_home", "care_home__address_details")
            .prefetch_related("images")
            .order_by("-pub_date")
        )

        care_home_id = self.request.GET.get("care_home", "").strip()
        location = self.request.GET.get("location", "").strip()
        near_lat = self._parse_float(self.request.GET.get("near_lat", "").strip())
        near_lon = self._parse_float(self.request.GET.get("near_lon", "").strip())
        has_near_coordinates = near_lat is not None and near_lon is not None

        if care_home_id:
            queryset = queryset.filter(care_home_id=care_home_id)

        if location and not has_near_coordinates:
            normalized_location = normalize_for_search(location)
            location_filter = (
                Q(care_home__address__icontains=location)
                | Q(care_home__address_details__search_text__icontains=normalized_location)
            )
            queryset = queryset.filter(location_filter)
            if not queryset.exists():
                try:
                    resolved_location = resolve_location_query_with_ban(location)
                except RuntimeError:
                    messages.warning(
                        self.request,
                        "Recherche de localisation BAN indisponible, résultats basés sur les données locales.",
                    )
                else:
                    resolved_terms = resolved_location["terms"] if resolved_location else []
                    for term in resolved_terms:
                        normalized_term = normalize_for_search(term)
                        if normalized_term:
                            location_filter |= Q(
                                care_home__address_details__search_text__icontains=normalized_term
                            )
                    queryset = Space.objects.filter(pub_date__lte=timezone.now(), status="available").select_related("care_home").order_by("-pub_date")
                    if care_home_id:
                        queryset = queryset.filter(care_home_id=care_home_id)
                    queryset = queryset.filter(location_filter)

        queryset = self._filter_around_me(queryset)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        view_mode = self.request.GET.get("view_mode", "list").strip().lower()
        if view_mode not in {"list", "map"}:
            view_mode = "list"

        list_params = self.request.GET.copy()
        list_params["view_mode"] = "list"
        map_params = self.request.GET.copy()
        map_params["view_mode"] = "map"

        context["care_home_options"] = (
            CareHome.objects.filter(space__pub_date__lte=timezone.now())
            .distinct()
            .order_by("name")
        )
        context["current_filters"] = {
            "care_home": self.request.GET.get("care_home", "").strip(),
            "location": self.request.GET.get("location", "").strip(),
            "radius_km": self.request.GET.get("radius_km", "").strip() or "20",
            "near_mode": self.request.GET.get("near_mode", "").strip(),
        }
        context["view_mode"] = view_mode
        context["list_view_url"] = f"{self.request.path}?{list_params.urlencode()}"
        context["map_view_url"] = f"{self.request.path}?{map_params.urlencode()}"
        context["around_me_active"] = self.around_me_active
        context["around_me_radius_km"] = self.around_me_radius_km
        location_parts = []
        if context["current_filters"]["location"]:
            location_parts.append(context["current_filters"]["location"])
        if self.around_me_active:
            location_parts.append(f"Autour de moi ({self.around_me_radius_km} km)")
        context["location_brief"] = " • ".join(location_parts) if location_parts else "Ville, département, région..."

        map_markers = []
        for space in context["space_list"]:
            address_details = space.care_home.address_details
            if not address_details or not address_details.has_coordinates:
                continue
            images = list(space.images.all())
            first_image = images[0] if images else None
            map_markers.append(
                {
                    "name": space.name,
                    "care_home_name": space.care_home.name,
                    "address": address_details.label or space.care_home.address,
                    "availability": space.availability,
                    "distance_km": getattr(space, "distance_km", None),
                    "image_url": first_image.image.url if first_image else "",
                    "image_alt": first_image.alt_text if first_image else "",
                    "detail_url": reverse("spaces:detail", args=[space.pk]),
                    "latitude": address_details.latitude,
                    "longitude": address_details.longitude,
                }
            )
        context["map_markers"] = map_markers
        context["map_markers_count"] = len(map_markers)
        context["map_center_lat"] = 48.8566
        context["map_center_lon"] = 2.3522
        if map_markers:
            context["map_center_lat"] = map_markers[0]["latitude"]
            context["map_center_lon"] = map_markers[0]["longitude"]
        return context

class DetailView(generic.DetailView):
    model = Space
    template_name = "spaces/detail.html"

    def get_queryset(self):
        """
        Excludes any spaces that aren't published yet.
        """
        return Space.objects.filter(pub_date__lte=timezone.now())

class ResultsView(generic.DetailView):
    model = Space
    template_name = "spaces/results.html"


def location_suggestions(request):
    query = request.GET.get("q", "").strip()
    if len(query) < 2:
        return JsonResponse({"results": []})

    try:
        suggestions = search_locations_with_ban(query)
    except RuntimeError:
        return JsonResponse({"results": []}, status=503)

    return JsonResponse({"results": suggestions})


def vote(request, space_id):
    return HttpResponse("You're voting on space %s." % space_id)
