from contracts.models import Contract
from django.shortcuts import get_object_or_404
from django.db.models import Q

def get_contract_by_id(contract_id):
    return get_object_or_404(Contract,pk=contract_id)

def get_active_contracts_for_user(user):
    contracts = Contract.objects.filter(status="active").filter(
        models.Q(client=user) | models.Q(freelancer=user)
    )
    return contracts

def get_contracts_as_client(user):
    contracts = Contract.objects.filter(client=user)
    return contracts

def get_contracts_as_freelancer(user):
    contracts = Contract.objects.filter(freelancer=user)
    return contracts

def get_submitted_contracts_for_client(user):
    contracts = Contract.objects.filter(status="submitted",client=user)
    return contracts

# actions or events that has happened in this contract
def get_contract_timeline(contract):
    return contract.events.order_by("created_at") # .events --> ContractEvent model