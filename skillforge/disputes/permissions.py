from rest_framework.exceptions import ValidationError
from submissions.models import Submission
from disputes.models import DisputeRequest

def can_request_dispute(contract,requester):
    if contract.dispute.exists():
        raise ValidationError(f"Dispute")

    if requester in [contract.freelancer,contract.client]:
        raise ValidationError(f"You are not permitted to open dispute for this contract")

def can_review_dispute_request(contract,reviewer):
    if not contract.dispute_request.exists():
        raise ValidationError(f"No dispute request found for this contract")

    if not reviewer.has_perm():
        raise ValidationError("Not permitted")

def can_open_dispute(contract,actor):
    if contract.disputes.exists():
        raise ValidationError(f"Dispute aleady opened by {actor}")
    
    if not contract.dispute_requests.exists():
        raise ValidationError(f"No dispute was requested for this contract.")
    
    if contract.dispute_request.status == DisputeRequest.DisputeRequestStatus.REJECTED:
        raise ValidationError(f"Dispute request is Rejected.")
    
    if contract.dispute_request.status == DisputeRequest.DisputeRequestStatus.PENDING:
        raise ValidationError(f"Dispute request is not yet reviewed.")

    if not actor.has_perm("contracts.resolve_dispute"):
        raise ValueError("Not permitted")

    last_submission = contract.submissions.order_by("-revision_number").first()

    if not last_submission:
        return False

    return (
        last_submission.revision_number >= contract.max_revisions
        and last_submission.status == Submission.SubmissionStatus.REJECTED
    )

def can_resolve_dispute(actor):
    if not actor.has_perm("contracts.resolve_dispute"):
        raise ValueError("Not permitted")