from django.contrib import admin
from django.contrib import messages

from .models import Address, CareHome, RecurringAvailability, Space, SpaceImage


class SpaceImageInline(admin.StackedInline):
    model = SpaceImage
    # extra = 3


class RecurringAvailabilityInline(admin.TabularInline):
    model = RecurringAvailability
    extra = 1

class SpaceAdmin(admin.ModelAdmin):
    inlines = [SpaceImageInline, RecurringAvailabilityInline]
    list_display = ("name", "care_home", "status", "publication_status", "pub_date")
    list_filter = ("status", "publication_status")


@admin.register(CareHome)
class CareHomeAdmin(admin.ModelAdmin):
    list_display = ("name", "address", "city", "department", "coordinates")
    search_fields = (
        "name",
        "address",
        "address_details__label",
        "address_details__city",
        "address_details__department_code",
        "address_details__department_name",
    )
    readonly_fields = ("address_details",)

    @admin.display(description="Ville")
    def city(self, obj):
        if obj.address_details:
            return obj.address_details.city
        return ""

    @admin.display(description="Département")
    def department(self, obj):
        if obj.address_details:
            code = obj.address_details.department_code
            name = obj.address_details.department_name
            if code and name:
                return f"{code} - {name}"
            return code or name
        return ""

    @admin.display(description="Coordonnées")
    def coordinates(self, obj):
        if obj.address_details and obj.address_details.latitude is not None and obj.address_details.longitude is not None:
            return f"{obj.address_details.latitude:.6f}, {obj.address_details.longitude:.6f}"
        return ""

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)

        if "address" not in form.changed_data and obj.address_details_id:
            return

        try:
            result = obj.refresh_address_details_from_ban(save=True)
        except RuntimeError as exc:
            self.message_user(request, str(exc), level=messages.WARNING)
            return

        if result is None:
            self.message_user(
                request,
                "Aucun résultat BAN trouvé pour cette adresse.",
                level=messages.WARNING,
            )


@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    list_display = ("label", "city", "department_code", "region_name", "postal_code", "latitude", "longitude", "ban_score")
    search_fields = ("raw_address", "label", "city", "department_code", "department_name", "region_name", "postal_code")


admin.site.register(Space, SpaceAdmin)
