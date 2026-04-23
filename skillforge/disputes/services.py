from contracts.models import Contract,ContractEvent
from disputes.models import Dispute, DisputeRequest
from contracts.events import trigger_event
from disputes.permissions import can_request_dispute,can_open_dispute,can_resolve_dispute,can_review_dispute_request
from django.db import transaction
from disputes.helpers import get_open_dispute_locked
from payments.services import refund_escrow,release_escrow,split_escrow
from rest_framework.exceptions import ValidationError
from django.utils import timezone

@transaction.atomic
def request_dispute(contract, requester,reason):
    contract = Contract.objects.select_for_update().get(id=contract.id)

    operation_key = f"dispute_requested:{contract.id}"

    existing = DisputeRequest.objects.filter(operation_key=operation_key).first()
    if existing:
        return existing

    can_request_dispute(contract,requester)

    request = DisputeRequest.objects.create(
        contract = contract,
        requester = requester,
        reason = reason
    )

    trigger_event(contract,requester,ContractEvent.ContractEventType.DISPUTE_OPENED,operation_key)
    return request


@transaction.atomic
def open_dispute(contract,actor,reason):
    contract = Contract.objects.select_for_update().get(id=contract.id)

    operation_key = f"dispute_opened:{contract.id}"

    existing = Dispute.objects.filter(operation_key=operation_key).first()
    if existing:
        return existing

    can_open_dispute(contract,actor)

    contract.transition_to(Contract.Status.DISPUTED)

    dispute = Dispute.objects.create(
        contract=contract,
        status=Dispute.Status.OPEN,
        opened_by=actor,
        reason=reason,
        operation_key = operation_key
    )

    trigger_event(contract,actor,ContractEvent.ContractEventType.DISPUTE_OPENED,operation_key)
    return dispute

def review_dispute_request(contract,actor,action):
    contract = Contract.objects.select_for_update().get(id=contract.id)

    operation_key = f"dispute_reviewed:{contract.id}"

    can_review_dispute_request(contract,actor)

    contract.dispute_request.reviewed_by = actor
    contract.dispute_request.reviewed_at = timezone.now()

    if action == DisputeRequest.DisputeRequestStatus.REJECTED:
        contract.dispute_request.status = DisputeRequest.DisputeRequestStatus.REJECTED
        contract.dispute_request.save()
        trigger_event(contract,actor,ContractEvent.ContractEventType.DISPUTE_REQUEST_REJECTED,operation_key)
        return contract.dispute_request
    
    if action != DisputeRequest.DisputeRequestStatus.APPROVED:
        raise ValidationError(f"Unknown review action - {action}")

    contract.dispute_request.status = DisputeRequest.DisputeRequestStatus.APPROVED
    ContractEvent.ContractEventType.DISPUTE_REQUEST_APPROVED
    contract.dispute_request.save()
    trigger_event(contract,actor,ContractEvent.ContractEventType.DISPUTE_REQUEST_APPROVED,operation_key)
    open_dispute(contract,actor,contract.dispute_request.reason)
    return contract.dispute_request


@transaction.atomic
def resolve_dispute_freelancer(contract,actor,reason):
    contract = Contract.objects.select_for_update().get(id=contract.id)
    operation_key = f"dispute_resolved:{contract.id}_freelancer"
    
    can_resolve_dispute(actor)
    dispute = get_open_dispute_locked(contract)

    if dispute.contract_id != contract.id:
        raise ValueError("Mismatch dispute and contract")

    release_escrow(contract.id)
    dispute.mark_resolved(actor=actor,resolution=Dispute.Resolution.FREELANCER)

    contract.transition_to(Contract.Status.PAID)
    trigger_event(contract,actor,ContractEvent.ContractEventType.DISPUTE_RESOLVED,operation_key)

    return contract

@transaction.atomic
def resolve_dispute_client(contract,actor):
    contract = Contract.objects.select_for_update().get(id=contract.id)
    operation_key = f"dispute_resolved:{contract.id}_client"

    can_resolve_dispute(actor)
    dispute = get_open_dispute_locked(contract)

    if dispute.contract_id != contract.id:
        raise ValueError("Mismatch dispute and contract")

    refund_escrow(contract.id)
    dispute.mark_resolved(actor=actor,resolution=Dispute.Resolution.CLIENT)

    contract.transition_to(Contract.Status.REFUNDED)
    trigger_event(contract,actor,ContractEvent.ContractEventType.DISPUTE_RESOLVED,operation_key)

    return contract

@transaction.atomic
def resolve_dispute_split(contract,actor,client_percent,freelancer_percent):
    contract = Contract.objects.select_for_update().get(id=contract.id)
    operation_key = f"dispute_resolved:{contract.id}_split"

    can_resolve_dispute(contract,actor)
    dispute = get_open_dispute_locked(contract)

    if dispute.contract_id != contract.id:
        raise ValueError("Mismatch dispute and contract")
    
    split_escrow(contract.id)

    contract.transition_to(Contract.Status.SPLIT_PAY)

    
    trigger_event(contract,actor,ContractEvent.ContractEventType.DISPUTE_RESOLVED,operation_key)

    return contract