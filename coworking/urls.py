from django.urls import path

from . import views

app_name = "coworking"

urlpatterns = [
    path("", views.CoworkingHomeView.as_view(), name="home"),
    path("projets/", views.CoworkingProjectListView.as_view(), name="project_list"),
]
