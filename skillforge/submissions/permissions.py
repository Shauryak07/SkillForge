from contracts.permissions import is_client,is_freelancer
from contracts.models import Contract
from submissions.models import Submission
from rest_framework.exceptions import ValidationError

def can_submit_work(user,contract,last_submission):

    if not is_freelancer(user,contract):
        raise ValidationError("Only assigned freelancer can submit work.")
    
    if contract.status != Contract.Status.IN_PROGRESS:
        raise ValidationError(f"Cannot submit work in state {contract.status}")

    if last_submission:
        if last_submission.status == Submission.SubmissionStatus.APPROVED:
            raise ValidationError("Work already approved.")

        if last_submission.revision_number >= contract.max_revisions:
            raise ValidationError("Max submissions reached.")

    return True

def can_approve_work(user, contract, submission):
    if not is_client(user, contract):
        raise ValidationError("Only contract client can approve work")

    if contract.status != Contract.Status.SUBMITTED:
        raise ValidationError(f"Cannot approve work in state {contract.status}")

    if not submission:
        raise ValidationError("No submission to approve")

    if submission.status != Submission.SubmissionStatus.PENDING:
        raise ValidationError("Invalid submission state")


    return True

def can_reject_work(user, contract, submission, feedback):
    if not is_client(user, contract):
        raise ValidationError("Only contract client can reject work")

    if contract.status != Contract.Status.SUBMITTED:
        raise ValidationError(f"Cannot reject work in state {contract.status}")

    if not submission:
        raise ValidationError("No submission to reject")

    if submission.status != Submission.SubmissionStatus.PENDING:
        raise ValidationError("Invalid submission state")

    if submission.revision_number >= contract.max_revisions:
        raise ValidationError("Final submission cannot be rejected.")

    if not feedback or not feedback.strip():
        raise ValidationError("Reason of rejection is required.")

    return True

