from payments.services import release_escrow,fund_contract,activate_contract
from contracts.models import ContractEvent


def run_handlers(contract,actor,event_type,contract_event):
    if contract_event.status == "PROCESSED":
        raise ("Contract event is already processed")

    try:
        contract_event.status = "PROCESSING"
        contract_event.save()

        if event_type == ContractEvent.ContractEventType.CONTRACT_ACTIVATED:
            # Notify contract is activated, when client will click "work started then it will go IN_PROGRESS "
            pass
        
        elif event_type == ContractEvent.ContractEventType.WORK_APPROVED:
            release_escrow(contract, actor)

        elif event_type == ContractEvent.ContractEventType.WORK_SUBMITTED:
            # Notify the client and his accept/reject will tell next state
            pass

        elif event_type == ContractEvent.ContractEventType.WORK_REJECTED:
            # it will go in progress as until n unless client creates a dispute
            pass

        # Payments

        elif event_type == ContractEvent.ContractEventType.CONTRACT_FUNDED:
            activate_contract(contract,actor)
            pass

        elif event_type == ContractEvent.ContractEventType.ESCROW_RELEASED:
            # Contract Completed 
            pass

        elif event_type == ContractEvent.ContractEventType.ESCROW_REFUNDED:
            # Close contract
            pass


    except Exception:
        contract_event.retry_count += 1
        contract_event.status = "FAILED"
        contract_event.save()
        raise ("something went wrong try again later please.")

