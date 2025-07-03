from django.urls import path
from carpool.views import rides_list, rides_create, rides_detail


app_name = "carpool"

urlpatterns = [
    path("", rides_list, name="list"),
    path("create/", rides_create, name="create"),
    path("detail/<int:pk>", rides_detail, name="detail"),
]
