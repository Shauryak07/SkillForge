from contracts.models import Contract,ContractEvent
from contracts.events import trigger_event


def create_contract(job, client, freelancer, amount):
    contract = Contract.objects.create(
        job=job,
        client=client,
        freelancer=freelancer,
        amount=amount,
    )
    trigger_event(contract,client,ContractEvent.ContractEventType.CONTRACT_CREATED)
    return contract
