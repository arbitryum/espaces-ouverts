from django.views.generic import TemplateView

from .models import CoworkingProject

class CoworkingHomeView(TemplateView):
    template_name = "coworking/home.html"


class CoworkingProjectListView(TemplateView):
    template_name = "coworking/projects.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["projects"] = CoworkingProject.objects.filter(
            is_published=True,
        ).select_related("care_home")
        return context
