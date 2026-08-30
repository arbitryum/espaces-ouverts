from django.contrib import admin

from .models import CoworkingProject


@admin.register(CoworkingProject)
class CoworkingProjectAdmin(admin.ModelAdmin):
    list_display = ("name", "organization_name", "location", "status", "is_published")
    list_filter = ("status", "is_published")
    search_fields = ("name", "organization_name", "location")
