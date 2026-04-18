from django.urls import path
from api.auth.views import *
from rest_framework_simplejwt.views import TokenObtainPairView,TokenRefreshView


urlpatterns = [

    # Contracts
    path("login/",TokenObtainPairView.as_view()),
    path("refresh/",TokenRefreshView.as_view()),
    path("register/",RegisterAPIView.as_view()),
    path("logout/",LogoutAPIView.as_view()),
   
]