from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.exceptions import MethodNotAllowed
from rest_framework.filters import SearchFilter,OrderingFilter

from api.bids.filters import BidFilter
from api.bids.permissions import IsJobOwner
from api.bids.serializers import BidSerializer,BidListSerializer
from bids.models import Bid
from bids.services import *
from jobs.models import Job


class BidViewSet(viewsets.ModelViewSet):
    queryset = Bid.objects.all()
    serializer_class = BidListSerializer
    filter_backends = [
        DjangoFilterBackend,
        OrderingFilter,
        SearchFilter
    ]
    filterset_class = BidFilter
    search_fields = ['proposal']
    ordering_fields = ['amount','-created_at']
    http_method_names = ["get", "post", "patch", "delete"]

    def get_serializer_class(self):
        if self.action in ["create", "partial_update"]:
            return BidSerializer
        return BidListSerializer

    def list(self,request):
        queryset = Bid.objects.filter(freelancer=request.user)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data,status.HTTP_200_OK)

    @action(detail=False, methods=['get'])
    def received_bids(self, request):
        queryset = Bid.objects.filter(job__client=request.user)
        queryset = self.filter_queryset(queryset)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data,status.HTTP_200_OK)

    def create(self,request):
        serializer = BidSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        job_id = serializer.validated_data['job_id']

        bid = place_bid(
            job=get_object_or_404(Job,id=job_id),
            actor=request.user,
            amount=serializer.validated_data['amount'],
            proposal=serializer.validated_data['proposal']
        )
        return Response({
            "message" : "Bid Placed",
            "bid_id" : bid.id,
            "job_id" : job_id,
        },status=status.HTTP_201_CREATED)  

    def update(self,request,*args,**kwargs):
        raise MethodNotAllowed("PUT")

    def partial_update(self,request,*args,**kwargs):
        bid = self.get_object()

        serializer=BidSerializer(data=request.data,partial=True)
        serializer.is_valid(raise_exception=True)

        updated_bid = update_bid(
            bid=bid,
            actor=request.user,
            **serializer.validated_data
        )      
        return Response({
            "message" : "Bid Updated",
            "bid_id" : bid.id,
        })  
    
    def destroy(self,request,*args,**kwargs):
        bid = self.get_object()

        withdraw_bid(bid,request.user)

        return Response({
            "message" : "Bid Withdrawed",
            "bid_id" : bid.id
        })

    @action(detail=True,methods=['post'])
    def accept(self,request,pk=None):
        bid = self.get_object()

        accepted_bid = accept_bid(bid,request.user)

        return Response({
            "message" : "Bid Accepted",
            "bid_id" : accepted_bid.id,
            "bid_status" : accepted_bid.status
        })
