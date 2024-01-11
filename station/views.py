from rest_framework import mixins, viewsets

from station.models import (
    TrainType,
    Train,
    Crew,
    Station,
    Route,
    Journey,
)
from station.serializers import (
    TrainTypeSerializer,
    TrainSerializer,
    CrewSerializer,
    StationSerializer,
    RouteSerializer,
    JourneySerializer,
)


class TrainTypeViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    viewsets.GenericViewSet,
):
    queryset = TrainType.objects.all()
    serializer_class = TrainTypeSerializer


class TrainViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    viewsets.GenericViewSet,
):
    queryset = Train.objects.all()
    serializer_class = TrainSerializer


class CrewViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    viewsets.GenericViewSet,
):
    queryset = Crew.objects.all()
    serializer_class = CrewSerializer


class StationViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    viewsets.GenericViewSet,
):
    queryset = Station.objects.all()
    serializer_class = StationSerializer


class RouteViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    viewsets.GenericViewSet,
):
    queryset = Route.objects.all()
    serializer_class = RouteSerializer


class JourneyViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    viewsets.GenericViewSet,
):
    queryset = Journey.objects.all()
    serializer_class = JourneySerializer
