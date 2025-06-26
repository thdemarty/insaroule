from django.contrib import admin
from django.urls import path, include
from carpool.views import rides_list

urlpatterns = [
    path("admin/", admin.site.urls),
    path("accounts/", include("accounts.urls", namespace="accounts")),
    path("", rides_list, name="rides_list"),
]
