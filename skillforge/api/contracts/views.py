from django.db.models.query_utils import Q
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import mixins, status, viewsets
from rest_framework.response import Response
from rest_framework.filters import OrderingFilter
from rest_framework.decorators import action

from api.contracts.filters import ContractFilter
from api.contracts.serializers import ContractSerializer
from contracts.models import Contract
from contracts.workflows import cancel_contract,activate_contract
from payments.services import fund_contract, release_escrow
from submissions.services import approve_work,submit_work,reject_work
from disputes.services import request_dispute


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
        },status=status.HTTP_200_OK)
    
    @action(detail=True,methods=['post'])
    def activate(self,request,pk=None):
        contract = self.get_object()

        activate_contract(contract,request.user)

        return Response({
            "message" : "Contract Activated",
            "contract_id" : contract.id
        },status=status.HTTP_200_OK)
    

    """ Payment """

    @action(detail=True,methods=['post'])
    def fund(self,request,pk=None):
        contract = self.get_object()

        fund_contract(contract=contract,actor=request.user)

        return Response({
            "message" : "Contract Funded",
            "contract_id" : contract.id
        },status=status.HTTP_200_OK)

    @action(detail=True,methods=['post'])
    def release_escrow(self,request,pk=None):
        contract = self.get_object()

        release_escrow(contract,request.user)

        return Response({
            "message" : "Released Escrow",
            "contract_id" : contract.id
        },status=status.HTTP_200_OK)
    
    @action(detail=True,methods=['post'])
    def release_escrow(self,request,pk=None):
        contract = self.get_object()

        release_escrow(contract,request.user)

        return Response({
            "message" : "Released Escrow",
            "contract_id" : contract.id
        },status=status.HTTP_200_OK)
    
    """ Submission """

    @action(detail=True,methods=['post'])
    def work_submit(self,request,pk=None):
        contract = self.get_object()
        message = request.data.get("message")

        submit_work(contract,request.user,message)

        return Response({
            "message" : "Work Submitted",
            "contract_id" : contract.id
        },status=status.HTTP_200_OK)
    
    @action(detail=True,methods=['post'])
    def work_approve(self,request,pk=None):
        contract = self.get_object()

        approve_work(contract,request.user)

        return Response({
            "message" : "Work Approved",
            "contract_id" : contract.id
        },status=status.HTTP_200_OK)

    @action(detail=True,methods=['post'])
    def work_reject(self,request,pk=None):
        contract = self.get_object()
        feedback = request.data.get("feedback")

        reject_work(contract,request.user,feedback)

        return Response({
            "message" : "Work Rejected",
            "contract_id" : contract.id
        },status=status.HTTP_200_OK)
    
    @action(detail=True,methods=['post'])
    def dispute_request(self,request,pk=None):
        contract = self.get_object()

        request = request_dispute(contract,request.user,reason)

        return Response({
            "message" : "Dispute Request submitted",
            "request_id" : request.id
        },status=status.HTTP_200_OK)


