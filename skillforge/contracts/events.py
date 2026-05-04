from contracts.models import ContractEvent
from contracts.handlers import run_handlers

def trigger_event(contract, actor,event,operation_key):
    contract_event = ContractEvent.objects.create(
        contract=contract,
        actor=actor,
        event_type=event,
        operation_key = operation_key
    )

    # run_handlers(contract, actor, event,contract_event)