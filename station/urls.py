from rest_framework import routers

from station.views import (
    TrainTypeViewSet,
    TrainViewSet,
    CrewViewSet,
    StationViewSet,
    RouteViewSet,
)

router = routers.DefaultRouter()
router.register("train_types", TrainTypeViewSet)
router.register("trains", TrainViewSet)
router.register("crews", CrewViewSet)
router.register("stations", StationViewSet)
router.register("routes", RouteViewSet)

urlpatterns = router.urls

app_name = "station"
