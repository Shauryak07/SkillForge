from submissions.models import Submission

def validate_wallet(wallet):
    if wallet.balance < 0  or wallet.locked_balance < 0:
        raise ValueError(f"Invalid wallet transaction.")
    
def validate_locked_balance(locked_balance,deduction_amount):
    if locked_balance < deduction_amount:
        raise ValueError("Insufficient locked balance.")
    
def validate_wallet_balance(wallet_balance,deduction_amount):
    if wallet_balance < deduction_amount:
        raise ValueError("Insufficient wallet balance.")

def validate_wallet_transaction_consistency(wallet):
    total = sum(
        wallet.transactions.values_list("amount",flat=True)
    )

    if wallet.balance != total:
        raise ValueError(
            f"Wallet balance mismatch. Expected {total} got {wallet.balance}"
        )

def get_latest_submission(contract):
    return (
        Submission.objects
        .select_for_update()
        .filter(contract=contract)
        .order_by('-revision_number')
        .first()
    )

