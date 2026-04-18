from api.contracts.serializers import ContractSerializer
from rest_framework import generics,serializers
from contracts.models import Contract
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated,IsAdminUser,AllowAny
from api.contracts.filters import ContractFilter
from rest_framework import filters
from django_filters.rest_framework import DjangoFilterBackend

class ContractListAPIView(generics.ListAPIView):
    queryset = Contract.objects.all()
    serializer_class = ContractSerializer
    filterset_class = ContractFilter
    filter_backends = [DjangoFilterBackend,filters.SearchFilter,filters.OrderingFilter]
    search_fields = ['title','amount','status','description']
    ordering_fields = ['amount']

class ContractDetailAPIView(generics.RetrieveAPIView):
    queryset = Contract.objects.all()
    serializer_class = ContractSerializer
    lookup_url_kwarg = "contract_id"

class ClientUserContractListAPIView(generics.ListCreateAPIView):
    queryset = Contract.objects.all()
    serializer_class = ContractSerializer
    filterset_class = ContractFilter
    filter_backends = [DjangoFilterBackend,filters.SearchFilter,filters.OrderingFilter]
    search_fields = ['title','amount','status','description']
    ordering_fields = ['amount']
    
    def get_queryset(self):
        qs =super().get_queryset()
        return qs.filter(client=self.request.user)


class FreelancerUserContractListAPIView(generics.ListAPIView):
    queryset = Contract.objects.all()
    serializer_class = ContractSerializer
    filterset_class = ContractFilter
    filter_backends = [DjangoFilterBackend,filters.SearchFilter,filters.OrderingFilter]
    search_fields = ['title','amount','status','description']
    ordering_fields = ['amount']
    
    def get_queryset(self):
        qs =super().get_queryset()
        return qs.filter(freelancer=self.request.user)

    