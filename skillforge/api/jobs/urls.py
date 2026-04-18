from django.urls import path
from api.jobs.views import *

urlpatterns = [
    path("", JobListAPIView.as_view()),
    path("create/",JobCreateAPIView.as_view()),
    path("<int:id>/update/",JobCreateAPIView.as_view()),
    path("<int:id>/cancel/",JobCreateAPIView.as_view()),
    path("<int:job_id>/",JobDetailAPIView.as_view()),
    path("client_user/",JobAsClientAPIView.as_view()),
]