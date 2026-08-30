from django.contrib import admin

from .models import EhpadProfile


@admin.register(EhpadProfile)
class EhpadProfileAdmin(admin.ModelAdmin):
    list_display = (
        "establishment_name",
        "contact_name",
        "user",
        "status",
        "participates_in_spaces",
        "participates_in_coworking",
    )
    list_filter = ("status", "participates_in_spaces", "participates_in_coworking")
    search_fields = ("establishment_name", "contact_name", "user__email", "user__username")

    def save_model(self, request, obj, form, change):
        obj.user.is_active = obj.status == EhpadProfile.STATUS_APPROVED
        obj.user.save(update_fields=["is_active"])
        super().save_model(request, obj, form, change)
