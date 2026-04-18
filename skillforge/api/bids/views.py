from rest_framework import generics,status
from rest_framework.views import APIView
from bids.models import Bid
from jobs.models import Job
from api.bids.serializers import BidSerializer,BidAcceptSerializer,BidPlaceSerializer
from api.bids.filters import BidFilter
from django_filters import filters
from django_filters.rest_framework import DjangoFilterBackend
from api.bids.permissions import IsJobOwner
from bids.services import accept_bid,place_bid
from rest_framework.response import Response
from django.core.exceptions import ValidationError as DjangoValidationError

class BidPlaceAPIView(APIView):
    def post(self,request):
        serializer = BidPlaceSerializer(data=request.data)

        if not serializer.is_valid():
            raise Response(serializer.errors,status=status.HTTP_200_OK)
        
        job_id = serializer.validated_data['job_id']
        amount = serializer.validated_data['amount']
        proposal = serializer.validated_data['proposal']

        try:
            job = Job.objects.get(id=job_id)
            updated_job = place_bid(job,request.user,amount,proposal)

            return Response({
                "message" : "Bid Placed Successfully",
                "job_id" : updated_job.id,
                "status" : updated_job.status
            },status=status.HTTP_200_OK)

        except Job.DoesNotExist:
            return Response({"error" : "Job not Found"},status=status.HTTP_400_BAD_REQUEST)

        except DjangoValidationError as e:
            return Response({"error" :  str(e)},status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            return Response({"error": "Something went wrong"},status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class BidAcceptAPIView(APIView):
    permission_classes = [IsJobOwner]
    def post(self,request):
        serializer = BidAcceptSerializer(data=request.data)

        if not serializer.is_valid():
            raise Respone(serializer.errors, status= status.HTTP_400_BAD_REQUEST)

        bid_id = serializer.validated_data['bid_id']

        try:
            bid = Bid.objects.get(id=bid_id)
            updated_bid = accept_bid(bid,request.user)

            return Response({
                "message": "Bid Accepted Successfully",
                "bid_id" : updated_bid.id,
                "status" : updated_bid.status
            },status=status.HTTP_200_OK)

        except Bid.DoesNotExist:
            return Response({"error":"Bid not Found"},status=status.HTTP_400_BAD_REQUEST)

        except DjangoValidationError as e:
            return Response({"error": str(e)},status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            return Response({"error": "Something went wrong"},status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class BidListAsClientAPIView(generics.RetrieveAPIView):
    serializer_class = BidSerializer
    lookup_url_kwarg = 'job_id'
    filterset_class = BidFilter
    filter_backends = [DjangoFilterBackend,filters.SearchFilter,filters.OrderingFilter]
    search_fields = ['amount','status']
    ordering_fields = ['amount','created_at']

    def get_queryset(self):
        user = self.request.user
        return Bid.objects.filter(job__client==user)
        

class BidListAsFreelancerAPIView(generics.ListAPIView):
    serializer_class = BidSerializer
    filterset_class = BidFilter
    filter_backends = [DjangoFilterBackend,filters.SearchFilter,filters.OrderingFilter]
    search_fields = ['amount','status']
    ordering_fields = ['amount','created_at']

    def get_queryset(self):
        user = self.request.user
        return Bid.objects.filter(freelancer=user)