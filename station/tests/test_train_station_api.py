from django.test import TestCase
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status

TRAIN_URL = reverse("station:train-list")
JOURNEY_URL = reverse("station:journey-list")


class UnauthenticatedTrainStationApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        res = self.client.get(TRAIN_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)
