from rest_framework import routers

from station.views import (
    TrainTypeViewSet,
    TrainViewSet,
)

router = routers.DefaultRouter()
router.register("train_types", TrainTypeViewSet)
router.register("trains", TrainViewSet)

urlpatterns = router.urls

app_name = "station"