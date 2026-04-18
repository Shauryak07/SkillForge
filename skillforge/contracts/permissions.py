from django.db.models import Q
from contracts.models import Contract
from django.core.exceptions import ValidationError

# Identity Checks

def is_client(user,contract):
    return contract.client == user

def is_freelancer(user,contract):
    return contract.freelancer == user

# Action Based Perms

# client side func
def can_activate_contract(user,contract):
    if not is_client(user,contract):
        raise ValidationError("Only contract client can activate contract")

    if contract.status != Contract.Status.FUNDED:
        raise ValidationError(f"Cannot activate contract in state {contract.status}")

    return True

def can_submit_work(user,contract):
    if not is_freelancer(user,contract):
        raise ValidationError("Only assigned freelancer can submit work.")
    
    if contract.status != Contract.Status.IN_PROGRESS:
        raise ValidationError(f"Cannot submit work in state {contract.status}")

    return True

def can_approve_work(user, contract):
    if not is_client(user,contract):
        raise ValidationError("Only contract client can approve work")
    
    if contract.status != Contract.Status.SUBMITTED:
        raise ValidationError(f"Cannot approve work in state {contract.status}")

    return True

def can_reject_work(user, contract):
    if not is_client(user,contract):
        raise ValidationError("Only contract client can reject work")
    
    if contract.status != Contract.Status.SUBMITTED:
        raise ValidationError(f"Cannot reject work in state {contract.status}")

    return True

# Later , because we have to give both client and freelancer this option but we cant give it like that so its function wil do later
def can_cancel_contract(user, contract):
    if not is_client(user,contract) or is_freelancer(user,contract):
        raise ValidationError("Only client or freelancer can cancel such contracts")

    if contract.status not in [Contract.Status.REJECTED, Contract.Status.DRAFT]:
        raise ValidationError(f"Can't cancel contract in current state - {contract.status}")

def can_view_contract(user, contract):
    return is_client(user,contract) or is_freelancer(user,contract)
    



#### MONEY RELATED

def can_fund_contract(user, contract):
    if not is_client(user,contract):
        raise ValidationError("Only contract client can fund contract")

    if contract.status != Contract.Status.DRAFT:
        raise ValidationError(f"Cannot fund contract in state {contract.status}")

    return True

def can_release_escrow(user, contract):
    if not is_client(user,contract):
        raise ValidationError("Only contract client can release escrow")

    if contract.status != Contract.Status.SUBMITTED:
        raise ValidationError(f"Cannot release escrow in state - {contract.status}")

    return True

""" Think and complete """
def can_refund_escrow(contract):
    if contract.status != Contract.Status.CANCELLED:
        raise ValidationError(f"Cannot refund escrow in current state - {contract.status}")

    return True

## DISPUTES

def can_open_dispute(contract,actor):
    if contract.disputes.exists():
        raise ValidationError(f"Dispute aleady opened by {actor}")

    if actor not in [contract.client,contract.freelancer]:
        raise ValidationError(f"You are not permitted to open dispute for this contract")

def can_resolve_dispute(contract,actor):
    if not actor.has_perm("contracts.resolve_dispute"):
        raise ValueError("Not permitted")
