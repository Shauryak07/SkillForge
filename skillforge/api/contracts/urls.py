from django.urls import path
from api.contracts.views import *

urlpatterns = [

    # Contracts
    path("",ContractListAPIView.as_view()),
    path("detail/<int:contract_id>/",ContractDetailAPIView.as_view()),
    path("client_user/",ClientUserContractListAPIView.as_view()),
    path("freelancer_user/",FreelancerUserContractListAPIView.as_view()),
    
]