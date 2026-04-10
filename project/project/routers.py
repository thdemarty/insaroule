from rest_framework import routers

from accounts.api.views import UserViewSet
from chat.api.views import ChatRequestViewSet
from carpool.api.views import RideListViewSet

router = routers.DefaultRouter()

router.register(r"conversations", ChatRequestViewSet)
router.register(r"rides", RideListViewSet)
router.register(r"me", UserViewSet, basename="me")
