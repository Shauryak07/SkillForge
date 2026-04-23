from contracts.models import Contract,ContractEvent, Dispute
from contracts.events import trigger_event
from contracts.permissions import can_open_dispute,can_resolve_dispute
from django.db import transaction
from domain.invariants import ensure_no_active_disputes

@transaction.atomic
def open_dispute(contract,actor,reason):
    contract = Contract.objects.select_for_update().get(id=contract.id)
    ensure_no_active_disputes(contract)
    can_open_dispute(contract,actor)

    dispute = Dispute.objects.create(
        contract=contract,
        status=Dispute.Status.OPEN,
        opened_by=actor,
        reason=reason
    )

    contract.transition_to(Contract.Status.DISPUTED)
    operation_key = f"dispute_opened_{contract.id}"
    trigger_event(contract,actor,ContractEvent.ContractEventType.DISPUTE_OPENED,operation_key)
    return dispute

@transaction.atomic
def resolve_dispute_freelancer(contract,actor):
    contract = Contract.objects.select_for_update().get(id=contract.id)
    can_resolve_dispute(contract,actor)

    contract.client.locked_balance -= contract.amount
    contract.freelancer.balance += contract.amount

    contract.transition_to(Contract.Status.PAID)
    operation_key = f"dispute_resolved_{contract.id}"
    trigger_event(contract,actor,ContractEvent.ContractEventType.DISPUTE_RESOLVED,operation_key)

    return contract

@transaction.atomic
def resolve_dispute_client(contract,actor):
    contract = Contract.objects.select_for_update().get(id=contract.id)
    can_resolve_dispute(contract,actor)

    contract.client.locked_balance -= contract.amount
    contract.client.balance += contract.amount

    contract.transition_to(Contract.Status.REFUNDED)
    operation_key = f"dispute_resolved_{contract.id}"
    trigger_event(contract,actor,ContractEvent.ContractEventType.DISPUTE_RESOLVED,operation_key)

    return contract

@transaction.atomic
def resolve_dispute_split(contract,actor,client_percent,freelancer_percent):
    contract = Contract.objects.select_for_update().get(id=contract.id)
    can_resolve_dispute(contract,actor)

    contract.client.locked_balance -= contract.amount
    contract.client.balance += contract.amount * (client_percent/100)
    contract.freelancer.balance += contract.amount * (freelancer_percent/100)

    contract.transition_to(Contract.Status.PAID)
    operation_key = f"dispute_resolved_{contract.id}"
    trigger_event(contract,actor,ContractEvent.ContractEventType.DISPUTE_RESOLVED,operation_key)

    return contract