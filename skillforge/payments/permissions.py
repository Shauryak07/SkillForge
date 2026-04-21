from contracts.permissions import is_client
from contracts.models import Contract
from django.core.exceptions import ValidationError

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
