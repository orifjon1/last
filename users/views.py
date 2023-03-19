from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.token_blacklist.models import OutstandingToken

from .models import Sector, CustomUser
from .serializer import UserSerializer, UserStatSerializer, UserProfileSerializer, SectorSerializer

from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import permissions

from .permission import IsDirector


class UserSignUpView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = UserSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


class LogoutView(APIView):
    authentication_classes = [JWTAuthentication]

    def post(self, request):
        token = request.auth
        OutstandingToken.blacklist(token)
        return Response({"detail": "Logout successful."})


class UserProfileView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        user = CustomUser.objects.get(id=request.user.id)
        serializer = UserProfileSerializer(user)
        return Response(serializer.data)

    def patch(self, request):
        user = CustomUser.objects.get(id=request.user.id)
        serializer = UserProfileSerializer(user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


class UserStatView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        users = CustomUser.objects.all()
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
    