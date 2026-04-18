from api.auth.serializers import *
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from django.contrib.auth import authenticate
from rest_framework.authtoken.models import Token
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.tokens import RefreshToken

 

class RegisterAPIView(APIView):
    permission_classes = [AllowAny,]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {"message": "User registered successfully"},
                status=status.HTTP_201_CREATED
            )

        return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)

# class LoginAPIView(TokenObtainPairView):
#     serializer_class = LoginSerializer


class LogoutAPIView(APIView):
    
    def post(self,request):
        try:
            refresh_token = request.data.get("refresh")
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response(
                {"message": "Logged Out"},
                status = status.HTTP_205_RESET_CONTENT
            )
        except:
            return Response(
                {"message": "Invalid token"},
                status= status.HTTP_400_BAD_REQUEST
            )