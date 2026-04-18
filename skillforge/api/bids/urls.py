from django.urls import path
from api.bids.views import *

urlpatterns = [
    path("job/<int:job_id>/",BidPlaceAPIView.as_view()),
    path("<int:bid_id>/aceept/",BidAcceptAPIView.as_view()),
    path("job/<int:job_id>/",BidListAsClientAPIView.as_view()),
    path("my/",BidListAsFreelancerAPIView.as_view()),
]