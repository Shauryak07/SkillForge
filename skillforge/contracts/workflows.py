from contracts.models import ContractEvent, Contract
from contracts.permissions import can_activate_contract, can_cancel_contract
from django.db import transaction
from contracts.events import trigger_event
from django.core.exceptions import ValidationError
from domain.invariants import ensure_no_active_disputes


def create_contract(job, client, freelancer, amount):
    if client != job.client:
        raise ValidationError("Only job owner can perform such actions")
    contract = Contract.objects.create(
        job=job,
        client=client,
        freelancer=freelancer,
        amount=amount,
    )
    trigger_event(contract,client,ContractEvent.ContractEventType.CONTRACT_CREATED)
    return contract


@transaction.atomic
def activate_contract(contract, actor):
    contract = Contract.objects.select_for_update().get(id=contract.id)

    can_activate_contract(actor,contract)
    contract.transition_to(Contract.Status.IN_PROGRESS)
    operation_key = f"activate_contract_{contract.id}"
    
    trigger_event(contract,actor,ContractEvent.ContractEventType.CONTRACT_ACTIVATED,operation_key)

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