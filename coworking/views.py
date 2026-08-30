from django.views.generic import TemplateView


class CoworkingHomeView(TemplateView):
    template_name = "coworking/home.html"
