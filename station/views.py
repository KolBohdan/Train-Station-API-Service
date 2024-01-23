from datetime import datetime
from typing import Type

from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema, OpenApiParameter
from rest_framework import mixins, viewsets, status

from django.db.models import F, Count
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response

from station.models import (
    TrainType,
    Train,
    Crew,
    Station,
    Route,
    Journey,
    Order,
)
from station.serializers import (
    TrainTypeSerializer,
    TrainSerializer,
    CrewSerializer,
    StationSerializer,
    RouteSerializer,
    JourneySerializer,
    TrainListSerializer,
    TrainDetailSerializer,
    RouteListSerializer,
    JourneyListSerializer,
    JourneyDetailSerializer,
    OrderSerializer,
    OrderListSerializer,
    TrainImageSerializer,
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
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet,
):
    queryset = Train.objects.select_related("train_type")
    serializer_class = TrainSerializer

    @staticmethod
    def _params_to_ints(qs) -> list[int]:
        """Converts a list of string IDs to a list of integers"""
        return [int(str_id) for str_id in qs.split(",")]

    def get_queryset(self):
        """Retrieve the trains with filters"""
        name = self.request.query_params.get("name")
        train_type = self.request.query_params.get("train_type")

        queryset = self.queryset

        if name:
            queryset = queryset.filter(name__icontains=name)

        if train_type:
            train_type_ids = self._params_to_ints(train_type)
            queryset = queryset.filter(train_type__id__in=train_type_ids)

        return queryset.distinct()

    def get_serializer_class(self) -> Type[
        TrainListSerializer |
        TrainDetailSerializer |
        TrainImageSerializer |
        TrainSerializer
    ]:
        if self.action == "list":
            return TrainListSerializer

        if self.action == "retrieve":
            return TrainDetailSerializer

        if self.action == "upload_image":
            return TrainImageSerializer

        return self.serializer_class

    @action(
        methods=["POST"],
        detail=True,
        url_path="upload-image",
        permission_classes=[IsAdminUser],
    )
    def upload_image(self, request, pk=None):
        """Endpoint for uploading image to specific train"""
        train = self.get_object()
        serializer = self.get_serializer(train, data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(
        parameters=[
            OpenApiParameter(
                "train_type",
                type={"type": "list", "items": {"type": "number"}},
                description="Filter by train_type id (ex. ?train_type=1,2)",
            ),
            OpenApiParameter(
                "name",
                type=OpenApiTypes.STR,
                description="Filter by train name (ex. ?name=Express)",
            ),
        ]
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)


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
    queryset = Route.objects.select_related("source", "destination")
    serializer_class = RouteSerializer

    def get_serializer_class(self) -> Type[
        RouteListSerializer |
        RouteSerializer
    ]:
        if self.action == "list":
            return RouteListSerializer

        return self.serializer_class


class JourneyViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet,
):
    queryset = (
        Journey.objects.all()
        .select_related("route__source", "route__destination")
        .annotate(
            tickets_available=(
                F("train__cargo_num") * F("train__places_in_cargo") - Count("tickets")
            )
        )
    )
    serializer_class = JourneySerializer

    @staticmethod
    def _params_to_ints(qs) -> list[int]:
        """Converts a list of string IDs to a list of integers"""
        return [int(str_id) for str_id in qs.split(",")]

    def get_queryset(self):
        """Retrieve the journeys with filters"""
        departure_time = self.request.query_params.get("departure_time")
        train = self.request.query_params.get("train")
        route = self.request.query_params.get("route")

        queryset = self.queryset

        if departure_time:
            departure_time = datetime.strptime(
                departure_time, "%Y-%m-%d"
            ).date()
            queryset = queryset.filter(departure_time__date=departure_time)

        if train:
            train_ids = self._params_to_ints(train)
            queryset = queryset.filter(train__id__in=train_ids)

        if route:
            route_ids = self._params_to_ints(route)
            queryset = queryset.filter(route__id__in=route_ids)

        return queryset.distinct()

    def get_serializer_class(self) -> Type[
        JourneyListSerializer |
        JourneyDetailSerializer |
        JourneySerializer
    ]:
        if self.action == "list":
            return JourneyListSerializer

        if self.action == "retrieve":
            return JourneyDetailSerializer

        return self.serializer_class

    @extend_schema(
        parameters=[
            OpenApiParameter(
                "train",
                type={"type": "list", "items": {"type": "number"}},
                description="Filter by train id (ex. ?train=2,4)",
            ),
            OpenApiParameter(
                "departure_time",
                type=OpenApiTypes.STR,
                description="Filter by departure time in format Y-m-d "
                            "(ex. ?departure_time=2024-02-20)",
            ),
            OpenApiParameter(
                "route",
                type={"type": "list", "items": {"type": "number"}},
                description="Filter by route id (ex. ?route=1,2)",
            ),
        ]
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)


class OrderPagination(PageNumberPagination):
    page_size = 10
    max_page_size = 100


class OrderViewSet(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    viewsets.GenericViewSet,
):
    queryset = Order.objects.prefetch_related(
        "tickets__journey__crew",
        "tickets__journey__route",
        "tickets__journey__train"
    )
    pagination_class = OrderPagination
    serializer_class = OrderSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user)

    def get_serializer_class(self) -> Type[
        OrderListSerializer |
        OrderSerializer
    ]:
        if self.action == "list":
            return OrderListSerializer

        return self.serializer_class

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
