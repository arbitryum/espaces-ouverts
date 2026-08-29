from django.urls import path

from . import views

app_name = "spaces"
urlpatterns = [
    # ex: /spaces/
    path("", views.IndexView.as_view(), name="index"),
    path("location-suggestions/", views.location_suggestions, name="location_suggestions"),
    # ex: /spaces/5/
    path("<int:pk>/", views.DetailView.as_view(), name="detail"),
    # ex: /spaces/5/results/
    path("<int:pk>/results/", views.ResultsView.as_view(), name="results"),
    # ex: /spaces/5/vote/
    path("<int:space_id>/vote/", views.vote, name="vote"),
]
