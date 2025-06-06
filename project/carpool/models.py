from django.db import models


class Ride(models.Model):
    driver = models.ForeignKey("accounts.User", on_delete=models.CASCADE)
    start_dt = models.DateTimeField()
    end_dt = models.DateTimeField()
    comment = models.TextField()

class Vehicle(models.Model):
    name = models.CharField(max_length=50)
    seats = models.PositiveIntegerField()
    color = models.CharField(max_length=50)