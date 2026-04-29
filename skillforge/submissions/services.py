from contracts.models import ContractEvent, Contract
from submissions.models import Submission
from submissions.permissions import *
from django.db import transaction
from contracts.events import trigger_event
from disputes.helpers import ensure_no_active_disputes
from django.utils import timezone

@transaction.atomic
def submit_work(contract, actor, message):
    contract = Contract.objects.select_for_update().get(id=contract.id)
    ensure_no_active_disputes(contract)
    
    last_submission = (
        Submission.objects
        .select_for_update()
        .filter(contract=contract)
        .order_by("-revision_number")
        .first()
    )

    can_submit_work(actor,contract,last_submission,message)

    submission = Submission.objects.create(
        contract=contract,
        submitted_by= actor,
        message=message,
        revision_number=(last_submission.revision_number if last_submission else 0) + 1
    )
    contract.current_submission = submission
    operation_key = f"work_submitted_{contract.id}_{submission.id}"
    contract.save(update_fields=["current_submission"])

    trigger_event(contract,actor,ContractEvent.ContractEventType.WORK_SUBMITTED,operation_key)

    return submission

@transaction.atomic
def approve_work(contract, actor):
    contract = Contract.objects.select_for_update().get(id=contract.id)
    ensure_no_active_disputes(contract)

    submission = contract.current_submission
    can_approve_work(actor,contract,submission)

    submission.status = Submission.SubmissionStatus.APPROVED
    submission.reviewed_by = actor
    submission.reviewed_at = timezone.now()
    submission.save()

    contract.transition_to(Contract.Status.COMPLETED)
    operation_key = f"approve_work_{contract.id}"

    trigger_event(contract,actor,ContractEvent.ContractEventType.WORK_APPROVED,operation_key)
    from payments.services import release_escrow
    release_escrow(contract,actor,operation_key)

@transaction.atomic
def reject_work(contract, actor,feedback):
    contract = Contract.objects.select_for_update().get(id = contract.id)
    ensure_no_active_disputes(contract)

    submission = contract.current_submission
    can_reject_work(actor, contract,submission,feedback)

    submission.status = Submission.SubmissionStatus.REJECTED
    submission.feedback = feedback
    submission.reviewed_by = actor
    submission.reviewed_at = timezone.now()
    submission.save()

    operation_key = f"reject_work_{contract.id}_{submission.id}"
    trigger_event(contract,actor,ContractEvent.ContractEventType.WORK_REJECTED,operation_key)
