from rest_framework.generics import GenericAPIView

from config.exceptions import CustomException
from .models import Sector, CustomUser
from .serializer import UserSerializer, UserStatSerializer, UserProfileSerializer, SectorSerializer, \
    RefreshTokenSerializer
from django.forms.models import model_to_dict

from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import permissions

from .permission import IsDirector


class UserSignUpView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        else:
            raise CustomException("To'g'ri ma'lumot kiriting!")


class LogoutView(GenericAPIView):
    serializer_class = RefreshTokenSerializer
    permission_classes = (permissions.IsAuthenticated, )

    def post(self, request, *args):
        sz = self.get_serializer(data=request.data)
        sz.is_valid(raise_exception=True)
        sz.save()
        return Response({"detail": "Logout successful."})


class UserProfileView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        serializer = UserProfileSerializer(instance=request.user)
        return Response(data=serializer.data)

    def patch(self, request):
        serializer = UserProfileSerializer(request.user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(data=serializer.data)
        return Response(data=serializer.errors)


class AllUserStatView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        users = CustomUser.objects.all().exclude(status='director')
        serializer = UserStatSerializer(users, many=True)
        return Response(serializer.data)


class SectorView(APIView):
    permission_classes = [permissions.IsAuthenticated, IsDirector]

    def get(self, request):
        sectors = Sector.objects.all()
        serializer = SectorSerializer(sectors, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = SectorSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


class SectorUpdateView(APIView):
    permission_classes = [permissions.IsAuthenticated, IsDirector]

    def get(self, request, id):
        sector = Sector.objects.get(id=id)
        serializer = SectorSerializer(sector)
        return Response(serializer.data)

    def put(self, request, id):
        sector = Sector.objects.get(id=id)
        serializer = SectorSerializer(instance=sector, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        else:
            raise CustomException("Yangi bo'lim nomini kiritishingiz kerak!")

    def delete(self, request, id):
        try:
            sector = Sector.objects.get(id=id)
        except Sector.DoesNotExist:
            raise CustomException("Bu bo'lim mavjud emas!")
        del sector
        return Response(data={'delete': 'deleted successfully!'})
