from rest_framework import viewsets
from accounts.api.serializers import UserSerializer


class UserViewSet(viewsets.ReadOnlyModelViewSet):
    """API endpoint that allows a user to get its information."""

    serializer_class = UserSerializer
    queryset = None

    def get_queryset(self):
        """This view should return a list of all the users for the currently authenticated user."""
        user = self.request.user
        return user.__class__.objects.filter(uuid=user.uuid)
