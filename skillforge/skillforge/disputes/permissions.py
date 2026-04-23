from rest_framework.exceptions import ValidationError
from submissions.models import Submission

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

def can_resolve_dispute(actor):
    if not actor.has_perm("contracts.resolve_dispute"):
        raise ValueError("Not permitted")