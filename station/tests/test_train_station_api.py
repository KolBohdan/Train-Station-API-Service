from django.contrib.auth import get_user_model
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
from station.serializers import TrainListSerializer

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
        name="Base"
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


def detail_url(train_id):
    return reverse("station:train-detail", args=[train_id])


class UnauthenticatedTrainApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        res = self.client.get(TRAIN_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthenticatedTrainApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            "test@test.com",
            "testpass",
        )
        self.client.force_authenticate(self.user)

    def test_list_trains(self):
        sample_train()
        sample_train()

        res = self.client.get(TRAIN_URL)

        trains = Train.objects.order_by("id")
        serializer = TrainListSerializer(trains, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_filter_trains_by_train_types(self):
        train_type1 = TrainType.objects.create(name="TrainType 1")
        train_type2 = TrainType.objects.create(name="TrainType 2")

        train1 = sample_train(name="Train 1", train_type=train_type1)
        train2 = sample_train(name="Train 2", train_type=train_type2)

        train3 = sample_train(name="Train with base type")

        res = self.client.get(
            TRAIN_URL, {"train_type": f"{train1.id},{train2.id}"}
        )

        serializer1 = TrainListSerializer(train1)
        serializer2 = TrainListSerializer(train2)
        serializer3 = TrainListSerializer(train3)

        self.assertIn(serializer1.data, res.data)
        self.assertIn(serializer2.data, res.data)
        self.assertNotIn(serializer3.data, res.data)

    def test_filter_trains_by_name(self):
        train1 = sample_train(name="Train")
        train2 = sample_train(name="Another Train")
        train3 = sample_train(name="No match")

        res = self.client.get(TRAIN_URL, {"name": "train"})

        serializer1 = TrainListSerializer(train1)
        serializer2 = TrainListSerializer(train2)
        serializer3 = TrainListSerializer(train3)

        self.assertIn(serializer1.data, res.data)
        self.assertIn(serializer2.data, res.data)
        self.assertNotIn(serializer3.data, res.data)


class UnauthenticatedJourneyApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        res = self.client.get(JOURNEY_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)
