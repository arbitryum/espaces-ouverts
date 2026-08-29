import datetime
import re
import unicodedata

from django.db import models
from django.utils import timezone


def normalize_for_search(value):
    if not value:
        return ""
    normalized = unicodedata.normalize("NFKD", value)
    ascii_text = normalized.encode("ascii", "ignore").decode("ascii")
    lowered = ascii_text.lower()
    words_only = re.sub(r"[^a-z0-9]+", " ", lowered)
    return " ".join(words_only.split())


class NonprofitOrganization(models.Model):
    name = models.CharField(max_length=200)
    address = models.CharField(max_length=200)
    def __str__(self):
        return self.name

class CareHome(models.Model):
    LEGAL_STATUS_CHOICES = [
        ("associatif", "Associatif"),
        ("public", "Public"),
        ("prive", "Privé"),
    ]
    
    name = models.CharField(max_length=200)
    address = models.CharField(max_length=200)
    address_details = models.ForeignKey(
        "Address",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="care_homes",
    )
    legal_status = models.CharField(
        max_length=20,
        choices=LEGAL_STATUS_CHOICES,
        blank=True,
        default="",
        help_text="Legal status of the organization"
    )
    contact_name = models.CharField(
        max_length=200,
        blank=True,
        default="",
        help_text="Name of the contact person"
    )
    contact_email = models.EmailField(
        blank=True,
        default="",
        help_text="Email address of the contact person"
    )
    group_name = models.CharField(
        max_length=200,
        blank=True,
        default="",
        help_text="Name of the parent organization or group"
    )

    def __str__(self):
        return self.name

    def refresh_address_details_from_ban(self, *, save=True):
        from spaces.services.geocoding import geocode_address_with_ban

        normalized_address = " ".join(self.address.split())
        if not normalized_address:
            self.address_details = None
            if save and self.pk:
                self.save(update_fields=["address_details"])
            return None

        geocoding_result = geocode_address_with_ban(normalized_address)
        if geocoding_result is None:
            return None

        address_details, _ = Address.objects.update_or_create(
            raw_address=normalized_address,
            defaults=geocoding_result,
        )
        self.address_details = address_details

        if save:
            update_fields = ["address_details"]
            if self.address != normalized_address:
                self.address = normalized_address
                update_fields.append("address")
            self.save(update_fields=update_fields)

        return address_details

class Space(models.Model):
    STATUS_CHOICES = [
        ("available", "Available"),
        ("full", "Full"),
        ("limited", "Limited"),
    ]
    
    care_home = models.ForeignKey(CareHome, on_delete=models.CASCADE)
    name = models.TextField()
    availability = models.TextField(default="")
    pub_date = models.DateTimeField("date published")
    description = models.TextField(default="")
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="available",
        help_text="Availability status of the space"
    )

    def __str__(self):
        return self.name + " (" + self.care_home.name + ")"

    def was_published_recently(self):
        now = timezone.now()
        return now - datetime.timedelta(days=1) <= self.pub_date <= now

    def get_first_image(self):
        """Returns the first image for this space, or None if no images exist."""
        return self.images.first()


class SpaceImage(models.Model):
    space = models.ForeignKey(Space, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(
        upload_to='spaces/%Y/%m/',
        help_text="Photo of the space"
    )
    alt_text = models.CharField(
        max_length=500,
        blank=True,
        default="",
        help_text="Alternative text for the image"
    )
    order = models.PositiveIntegerField(
        default=0,
        help_text="Display order (lower numbers appear first)"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['order', 'created_at']

    def __str__(self):
        return f"{self.space.name} - Image {self.order}"


class Address(models.Model):
    DEFAULT_EMBED_DELTA = 0.01

    raw_address = models.CharField(max_length=255, unique=True)
    label = models.CharField(max_length=255, blank=True, default="")
    city = models.CharField(max_length=120, blank=True, default="")
    postal_code = models.CharField(max_length=16, blank=True, default="")
    city_code = models.CharField(max_length=16, blank=True, default="")
    department_code = models.CharField(max_length=8, blank=True, default="")
    department_name = models.CharField(max_length=120, blank=True, default="")
    region_name = models.CharField(max_length=120, blank=True, default="")
    search_text = models.TextField(blank=True, default="")
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    ban_id = models.CharField(max_length=64, blank=True, default="")
    ban_score = models.FloatField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["city", "postal_code", "label"]

    def __str__(self):
        return self.label or self.raw_address

    def save(self, *args, **kwargs):
        self.search_text = normalize_for_search(
            " ".join(
                [
                    self.raw_address,
                    self.label,
                    self.city,
                    self.postal_code,
                    self.city_code,
                    self.department_code,
                    self.department_name,
                    self.region_name,
                ]
            )
        )
        update_fields = kwargs.get("update_fields")
        if update_fields is not None:
            kwargs["update_fields"] = set(update_fields) | {"search_text"}
        super().save(*args, **kwargs)

    @property
    def has_coordinates(self):
        return self.latitude is not None and self.longitude is not None

    @property
    def osm_bbox(self):
        if not self.has_coordinates:
            return ""
        delta = self.DEFAULT_EMBED_DELTA
        min_lon = self.longitude - delta
        min_lat = self.latitude - delta
        max_lon = self.longitude + delta
        max_lat = self.latitude + delta
        return f"{min_lon:.6f},{min_lat:.6f},{max_lon:.6f},{max_lat:.6f}"

    @property
    def osm_map_url(self):
        if not self.has_coordinates:
            return ""
        return (
            "https://www.openstreetmap.org/"
            f"?mlat={self.latitude}&mlon={self.longitude}"
            f"#map=16/{self.latitude}/{self.longitude}"
        )

    @property
    def osm_embed_url(self):
        if not self.has_coordinates:
            return ""
        return (
            "https://www.openstreetmap.org/export/embed.html"
            f"?bbox={self.osm_bbox}&layer=mapnik&marker={self.latitude}%2C{self.longitude}"
        )
