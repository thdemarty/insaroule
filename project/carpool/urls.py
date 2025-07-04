from django.urls import path
from carpool.views import (
    rides_list,
    rides_create,
    rides_detail,
    api_auto_completion,
    api_routing,
)


app_name = "carpool"

urlpatterns = [
    path("", rides_list, name="list"),
    path("create/", rides_create, name="create"),
    path("<uuid:pk>/", rides_detail, name="detail"),
    # API endpoints
    path("api/completion/", api_auto_completion, name="completion"),
    path("api/routing/", api_routing, name="routing"),
]
