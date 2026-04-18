from contracts.models import ContractEvent
from contracts.handlers import run_handlers

def trigger_pay_event(contract, actor,event_type):
    contract_event = ContractEvent.objects.create(
        contract=contract,
        actor=actor,
        event_type=event_type
    )

    run_handlers(contract,actor,event_type,contract_event)
    
