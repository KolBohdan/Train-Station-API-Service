from django.test import TestCase
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status

from station.models import (
    TrainType,
    Train,
    Station,
    Route,
    Crew,
    Journey,
)

TRAIN_URL = reverse("station:train-list")
JOURNEY_URL = reverse("station:journey-list")


def sample_station(**params):
    defaults = {
        "name": "Sample station",
        "latitude": 10.2,
        "longitude": 15.1
    }

    defaults.update(params)

    return Station.objects.create(**defaults)


def sample_route(**params):
    source = sample_station(name="First station")
    destination = sample_station(name="Second station")

    defaults = {
        "source": source,
        "destination": destination,
        "distance": 500
    }

    defaults.update(params)

    return Route.objects.create(**defaults)


def sample_train(**params):
    train_type = TrainType.objects.create(
        name="Test type"
    )

    defaults = {
        "name": "Sample train",
        "cargo_num": 4,
        "places_in_cargo": 20,
        "train_type": train_type
    }
    defaults.update(params)

    return Train.objects.create(**defaults)


def sample_journey(**params):
    train = sample_train()
    route = sample_route()
    crew = Crew.objects.create(
        first_name="Testname",
        last_name="Testlastname"
    )

    defaults = {
        "route": route,
        "train": train,
        "departure_time": "2024-01-18 15:00:00",
        "arrival_time": "2024-01-19 10:00:00",
        "crew": crew
    }
    defaults.update(params)

    return Journey.objects.create(**defaults)


class UnauthenticatedTrainStationApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        res = self.client.get(TRAIN_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)
