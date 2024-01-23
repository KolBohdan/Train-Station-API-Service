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
from station.serializers import (
    TrainListSerializer,
    TrainDetailSerializer,
    JourneyListSerializer,
    JourneyDetailSerializer,
)

TRAIN_URL = reverse("station:train-list")
JOURNEY_URL = reverse("station:journey-list")


def sample_station(**params):
    defaults = {"name": "Sample station", "latitude": 10.2, "longitude": 15.1}

    defaults.update(params)

    return Station.objects.create(**defaults)


def sample_route(**params):
    source = sample_station(name="First station")
    destination = sample_station(name="Second station")

    defaults = {"source": source, "destination": destination, "distance": 500}

    defaults.update(params)

    return Route.objects.create(**defaults)


def sample_train(**params):
    train_type = TrainType.objects.create(name="Base")

    defaults = {
        "name": "Sample train",
        "cargo_num": 4,
        "places_in_cargo": 20,
        "train_type": train_type,
    }
    defaults.update(params)

    return Train.objects.create(**defaults)


def sample_journey(**params):
    train = sample_train()
    route = sample_route()

    defaults = {
        "route": route,
        "train": train,
        "departure_time": "2024-01-18T15:00:00+02:00",
        "arrival_time": "2024-01-19T10:00:00+02:00",
    }
    defaults.update(params)

    journey = Journey.objects.create(**defaults)

    journey.tickets_available = train.cargo_num * train.places_in_cargo

    return journey


def detail_train_url(train_id):
    return reverse("station:train-detail", args=[train_id])


def detail_journey_url(journey_id):
    return reverse("station:journey-detail", args=[journey_id])


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
            TRAIN_URL, {"train_type": f"{train_type1.id},{train_type2.id}"}
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

    def test_retrieve_train_detail(self):
        train = sample_train()

        url = detail_train_url(train.id)
        res = self.client.get(url)

        serializer = TrainDetailSerializer(train)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_create_train_forbidden(self):
        train_type = TrainType.objects.create(name="Test")

        payload = {
            "name": "Train",
            "cargo_num": 10,
            "places_in_cargo": 15,
            "train_type": train_type,
        }
        res = self.client.post(TRAIN_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)


class UnauthenticatedJourneyApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        res = self.client.get(JOURNEY_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthenticatedJourneyApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            "test@test.com",
            "testpass",
        )
        self.client.force_authenticate(self.user)

    def test_list_journeys(self):
        res = self.client.get(JOURNEY_URL)

        journeys = Journey.objects.order_by("id")
        serializer = JourneyListSerializer(journeys, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_filter_journeys_by_routes(self):
        route1 = sample_route(distance=111)
        route2 = sample_route(distance=222)
        route3 = sample_route(distance=333)

        journey1 = sample_journey(route=route1)
        journey2 = sample_journey(route=route2)
        journey3 = sample_journey(route=route3)

        res = self.client.get(
            JOURNEY_URL, {"route": f"{route1.id}, {route2.id}"}
        )

        serializer1 = JourneyListSerializer(journey1)
        serializer2 = JourneyListSerializer(journey2)
        serializer3 = JourneyListSerializer(journey3)

        self.assertIn(serializer1.data, res.data)
        self.assertIn(serializer2.data, res.data)
        self.assertNotIn(serializer3.data, res.data)

    def test_filter_journeys_by_trains(self):
        train1 = sample_train(name="Train 1")
        train2 = sample_train(name="Train 2")
        train3 = sample_train(name="Train 3")

        journey1 = sample_journey(train=train1)
        journey2 = sample_journey(train=train2)
        journey3 = sample_journey(train=train3)

        res = self.client.get(
            JOURNEY_URL, {"train": f"{train1.id}, {train2.id}"}
        )

        serializer1 = JourneyListSerializer(journey1)
        serializer2 = JourneyListSerializer(journey2)
        serializer3 = JourneyListSerializer(journey3)

        self.assertIn(serializer1.data, res.data)
        self.assertIn(serializer2.data, res.data)
        self.assertNotIn(serializer3.data, res.data)

    def test_filter_journeys_by_departure_time(self):
        departure_time = "2024-01-18"

        journey1 = sample_journey()
        journey2 = sample_journey(departure_time="2000-01-18T15:00:00+02:00")

        res = self.client.get(JOURNEY_URL, {"departure_time": departure_time})

        serializer1 = JourneyListSerializer(journey1)
        serializer2 = JourneyListSerializer(journey2)

        self.assertIn(serializer1.data, res.data)
        self.assertNotIn(serializer2.data, res.data)

    def test_retrieve_journey_detail(self):
        journey = sample_journey()

        url = detail_journey_url(journey.id)
        res = self.client.get(url)

        serializer = JourneyDetailSerializer(journey)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_create_journey_forbidden(self):
        route = sample_route()
        train = sample_train()
        departure_time = "2024-01-18T15:00:00+02:00"
        arrival_time = "2024-01-19T15:00:00+02:00"
        crew = Crew.objects.create(
            first_name="Testname", last_name="Testlastname"
        )

        payload = {
            "route": route,
            "train": train,
            "departure_time": departure_time,
            "arrival_time": arrival_time,
            "crew": crew.id,
        }
        res = self.client.post(JOURNEY_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)


class AdminTrainApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            "admin@admin.com", "testpass", is_staff=True
        )
        self.client.force_authenticate(self.user)

    def test_create_train(self):
        train_type = TrainType.objects.create(name="Test type")

        payload = {
            "name": "Test train",
            "cargo_num": 4,
            "places_in_cargo": 20,
            "train_type": train_type.id,
        }
        res = self.client.post(TRAIN_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)


class AdminJourneyApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            "admin@admin.com", "testpass", is_staff=True
        )
        self.client.force_authenticate(self.user)

    def test_create_journey(self):
        route = sample_route()
        train = sample_train()
        departure_time = "2024-01-18T15:00:00+02:00"
        arrival_time = "2024-01-19T15:00:00+02:00"
        crew1 = Crew.objects.create(
            first_name="Testname1", last_name="Testlastname1"
        )
        crew2 = Crew.objects.create(
            first_name="Testname2", last_name="Testlastname2"
        )

        payload = {
            "route": route.id,
            "train": train.id,
            "departure_time": departure_time,
            "arrival_time": arrival_time,
            "crew": [crew1.id, crew2.id],
        }
        res = self.client.post(JOURNEY_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
