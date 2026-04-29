from contracts.permissions import is_client
from contracts.models import Contract,ContractEvent
from rest_framework.exceptions import ValidationError

def can_fund_contract(actor, contract):
    if not is_client(actor,contract):
        raise ValidationError("Only contract client can fund contract")

    if contract.status != Contract.Status.DRAFT:
        raise ValidationError(f"Cannot fund contract in state {contract.status}")

    return True

def can_release_escrow(actor, contract):
    if not is_client(actor,contract) or actor.has_perm():
        raise ValidationError("Only contract client can release escrow")

    if contract.status != Contract.Status.SUBMITTED:
        raise ValidationError(f"Cannot release escrow in state - {contract.status}")
    
    if contract.events == ContractEvent.ContractEventType.DISPUTE_REQUESTED:
        raise ValidationError(f"Action blocked due to pending dispute request.")

    return True

""" Think and complete """
def can_refund_escrow(actor,contract):
    if not actor.has_perm():
        raise ValidationError("You are not permitted to peform this action")
    
    if contract.status != Contract.Status.DISPUTED:
        raise ValidationError(f"Cannot refund from the state {contract.status}")

    if contract.events == ContractEvent.ContractEventType.DISPUTE_REQUESTED:
        raise ValidationError(f"Cannot refund escrow until pending dispute request is reviewed.")

    return True

def can_split_escrow(actor,contract):
    if not actor.has_perm():
        raise ValidationError("You are not permitted to peform this action")
    
    if contract.status != Contract.Status.DISPUTED:
        raise ValidationError(f"Cannot split escrow in the state {contract.status}")

    return True
