from django.urls import path

from . import views

app_name = "coworking"

urlpatterns = [
    path("", views.CoworkingHomeView.as_view(), name="home"),
]
