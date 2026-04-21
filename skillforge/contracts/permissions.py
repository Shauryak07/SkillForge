from contracts.models import Contract
from django.core.exceptions import ValidationError
from submissions.models import Submission

# Identity Checks
def is_client(user,contract):
    return contract.client == user

def is_freelancer(user,contract):
    return contract.freelancer == user

# client side func
def can_activate_contract(user,contract):
    if not is_client(user,contract):
        raise ValidationError("Only contract client can activate contract")

    if contract.status != Contract.Status.FUNDED:
        raise ValidationError(f"Cannot activate contract in state {contract.status}")

    return True

# Later , because we have to give both client and freelancer this option but we cant give it like that so its function wil do later
def can_cancel_contract(user, contract):
    if not is_client(user,contract) or is_freelancer(user,contract):
        raise ValidationError("Only client or freelancer can cancel such contracts")

    if contract.status not in [Contract.Status.REJECTED, Contract.Status.DRAFT]:
        raise ValidationError(f"Can't cancel contract in current state - {contract.status}")

def can_view_contract(user, contract):
    return is_client(user,contract) or is_freelancer(user,contract)
    

## DISPUTES

def can_open_dispute(contract,actor):
    if contract.disputes.exists():
        raise ValidationError(f"Dispute aleady opened by {actor}")

    if actor not in [contract.client,contract.freelancer]:
        raise ValidationError(f"You are not permitted to open dispute for this contract")
    
    last_submission = contract.submissions.order_by("-revision_number").first()

    if not last_submission:
        return False

    return (
        last_submission.revision_number >= contract.max_revisions
        and last_submission.status == Submission.SubmissionStatus.REJECTED
    )

def can_resolve_dispute(contract,actor):
    if not actor.has_perm("contracts.resolve_dispute"):
        raise ValueError("Not permitted")
