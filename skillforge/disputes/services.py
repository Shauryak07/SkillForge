from contracts.models import Contract,ContractEvent
from disputes.models import Dispute
from contracts.events import trigger_event
from disputes.permissions import can_open_dispute,can_resolve_dispute
from django.db import transaction
from disputes.helpers import ensure_no_active_disputes,get_open_dispute_locked
from payments.services import refund_escrow,release_escrow,split_escrow

@transaction.atomic
def open_dispute(contract,actor,reason):
    contract = Contract.objects.select_for_update().get(id=contract.id)

    operation_key = f"dispute_opened:{contract.id}"

    existing = Dispute.objects.filter(operation_key=operation_key).first()
    if existing:
        return existing

    ensure_no_active_disputes(contract)
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