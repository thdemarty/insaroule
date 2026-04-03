from carpool.models.ride import Ride
from carpool.models import Location
from rest_framework import serializers


class CityLocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Location
        fields = ["city"]


class SmallRideSerializer(serializers.ModelSerializer):
    start_loc = CityLocationSerializer(read_only=True)
    end_loc = CityLocationSerializer(read_only=True)

    class Meta:
        model = Ride
        fields = ["uuid", "start_loc", "end_loc", "start_dt", "end_dt"]
