from django.db.models.query_utils import Q
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, mixins, serializers, status, viewsets
from rest_framework.response import Response
from rest_framework.filters import OrderingFilter
from rest_framework.decorators import action

from api.contracts.filters import ContractFilter
from api.contracts.serializers import ContractSerializer
from contracts.models import Contract
from contracts.workflows import cancel_contract


class ContractViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet
):
    serializer_class = ContractSerializer
    filter_backends = [
        DjangoFilterBackend,
        OrderingFilter
    ]
    filterset_class = ContractFilter
    ordering_fields = ['amount','-created_at']

    def get_queryset(self):
        user = self.request.user

        role = self.request.query_params.get("role")

        qs = Contract.objects.filter(Q(client=user) | Q(freelancer=user))

        if role == "client":
            qs = qs.filter(client=user)
        elif role == "freelancer":
            qs = qs.filter(freelancer=user)
        else:
            qs = qs.filter(client=user)

        return qs
    
    @action(detail=True,methods=['post'])
    def cancel(self,request,pk=None):
        contract = self.get_object()

        cancel_contract(contract,request.user)

        return Response({
            "message" : "Contract Cancelled",
            "contract_id" : contract.id
        })

