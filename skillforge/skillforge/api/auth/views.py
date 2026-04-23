from api.auth.serializers import RegisterSerializer, LogoutSerializer
from rest_framework import status
from rest_framework.response import Response
from rest_framework.generics import GenericAPIView
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.tokens import RefreshToken

 

class RegisterAPIView(GenericAPIView):
    permission_classes = [AllowAny,]
    serializer_class = RegisterSerializer

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        serializer.save()

        return Response(
            {"message": "User registered successfully"},
            status=status.HTTP_201_CREATED
        )

class LogoutAPIView(GenericAPIView):
    serializer_class = LogoutSerializer

    def post(self,request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        refresh_token = serializer.validated_data['refresh']

        try:
            token = RefreshToken(refresh_token)
            token.blacklist()
            
        except Exception:
            return Response({"message": "Invalid or expired token"},)

        return Response(
                {"message": "Logged Out"},
                status = status.HTTP_205_RESET_CONTENT
            )