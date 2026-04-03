from rest_framework import routers

from chat.api.views import ChatRequestViewSet


router = routers.DefaultRouter()

router.register(r"conversations", ChatRequestViewSet)
