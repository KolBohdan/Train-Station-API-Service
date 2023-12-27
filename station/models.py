from django.db import models


class Station(models.Model):
    name = models.CharField(max_length=255)
    latitude = models.FloatField()
    longitude = models.FloatField()

    def __str__(self) -> str:
        return self.name


class Route(models.Model):
    source = models.ForeignKey(
        to=Station,
        on_delete=models.CASCADE,
        related_name="route_sources"
    )
    destination = models.ForeignKey(
        to=Station,
        on_delete=models.CASCADE,
        related_name="route_destinations"
    )
    distance = models.IntegerField()

    def __str__(self) -> str:
        return f"{self.source} -> {self.destination}"
