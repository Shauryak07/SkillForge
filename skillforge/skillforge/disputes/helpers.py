from disputes.models import Dispute

def get_open_dispute_locked(contract):
    dispute = (
        Dispute.objects
        .select_for_update()
        .filter(contract=contract, status=Dispute.Status.OPEN)
        .first()
    )
    if not dispute:
        raise ValueError("No active dispute found")
    return dispute
    
def ensure_no_active_disputes(contract):
    exists = Dispute.objects.filter(contract=contract,status=Dispute.Status.OPEN).exists()

    if exists:
        raise ValueError("Active disputes exists for this contract ")