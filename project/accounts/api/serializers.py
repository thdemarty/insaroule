from rest_framework import serializers
from accounts.models import User


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["uuid", "username", "email"]


class UsernameUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["uuid", "username"]
