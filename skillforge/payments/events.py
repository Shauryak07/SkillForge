from contracts.models import ContractEvent


def trigger_pay_event(contract, actor,event_type):
    contract_event = ContractEvent.objects.create(
        contract=contract,
        actor=actor,
        event_type=event_type
    )

    
    
