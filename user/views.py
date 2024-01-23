from rest_framework import generics
from rest_framework.permissions import IsAuthenticated, AllowAny

from train_station_service.settings import AUTH_USER_MODEL
from user.serializers import UserSerializer


class CreateUserView(generics.CreateAPIView):
    serializer_class = UserSerializer
    permission_classes = (AllowAny,)


class ManageUserView(generics.RetrieveUpdateAPIView):
    serializer_class = UserSerializer
    permission_classes = (IsAuthenticated,)

    def get_object(self) -> AUTH_USER_MODEL:
        return self.request.user
