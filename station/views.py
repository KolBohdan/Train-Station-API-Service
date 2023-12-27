from rest_framework import mixins, viewsets

from station.models import (
    TrainType,
    Train,
)
from station.serializers import (
    TrainTypeSerializer,
    TrainSerializer,
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
