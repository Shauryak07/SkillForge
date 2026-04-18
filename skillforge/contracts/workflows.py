from contracts.models import ContractEvent, Contract, Submission
from contracts.permissions import *
from django.db import transaction
from django.db.models import Max
from contracts.events import trigger_event

@transaction.atomic
def activate_contract(contract, actor):
    contract = Contract.objects.select_for_update().get(id=contract.id)

    can_activate_contract(actor,contract)
    contract.transition_to(Contract.Status.IN_PROGRESS)
    operation_key = f"activate_contract_{contract.id}"
    
    trigger_event(contract,actor,ContractEvent.ContractEventType.CONTRACT_ACTIVATED,operation_key)


@transaction.atomic
def submit_work(contract, actor, message):
    contract = Contract.objects.select_for_update().get(id=contract.id)
    ensure_no_active_disputes(contract)
    can_submit_work(actor,contract)
    
    last_submission = contract.submissions.order_by("-revision_number").first()
    submission = Submission.objects.create(
        contract=contract,
        submitted_by= actor,
        message=message,
        revision_number=(last_submission.revision_number if last_submission else 0) + 1
    )
    contract.current_submission = submission
    contract.transition_to(Contract.Status.SUBMITTED)
    operation_key = f"work_submitted_{contract.id}_{submission.id}"
    contract.save(update_fields=["status","current_submission"])

    trigger_event(contract,actor,ContractEvent.ContractEventType.WORK_SUBMITTED,operation_key)

    return submission

@transaction.atomic
def approve_work(contract, actor):
    contract = Contract.objects.select_for_update().get(id=contract.id)
    ensure_no_active_disputes(contract)

    can_approve_work(actor,contract)

    submission = contract.current_submission
    if not submission:
        raise ValidationError("No submission to approve")

    submission.status = Submission.SubmissionStatus.APPROVED
    submission.save(update_fields=["status"])

    contract.transition_to(Contract.Status.CONTRACT_APPROVED)
    operation_key = f"approve_work_{contract.id}"

    trigger_event(contract,actor,ContractEvent.ContractEventType.WORK_APPROVED,operation_key)
    from payments.services import release_escrow
    release_escrow(contract,actor)

@transaction.atomic
def reject_work(contract, actor):
    contract = Contract.objects.select_for_update().get(id = contract.id)
    ensure_no_active_disputes(contract)
    can_reject_work(actor, contract)

    submission = contract.current_submission
    submission.status = Submission.SubmissionStatus.REJECTED
    submission.save(update_fields=["status"])

    contract.transition_to(Contract.Status.IN_PROGRESS)
    operation_key = f"reject_work_{contract.id}_{submission.id}"
    trigger_event(contract,actor,ContractEvent.ContractEventType.WORK_REJECTED,operation_key)

# Unbuilt can_cancel_contract function
@transaction.atomic
def cancel_contract(contract, actor):
    contract = Contract.objects.select_for_update().get(id = contract.id)
    ensure_no_active_disputes(contract)

    can_cancel_contract(actor, contract)
    contract.transition_to(Contract.Status.CANCELLED)
    operation_key = f"cancel_contract_{contract.id}"

    trigger_event(contract,actor,ContractEvent.ContractEventType.WORK_REJECTED,operation_key)
    return contract



# Later

# def reopen_contract(contract, actor):
#     pass

# def raise_dispute(contract, actor):
#     pass