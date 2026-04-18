
def validate_wallet(wallet):
    if wallet.balance < 0  or wallet.locked_balance < 0:
        raise ValueError(f"Invalid wallet transaction.")

def ensure_no_active_disputes(contract):
    active_dispute = contract.disputes.filter(status="open").count()

    if active_dispute >= 1:
        return False

def validate_wallet_transaction_consistency(wallet):
    total = sum(
        wallet.transactions.values_list("amount",flat=True)
    )

    if wallet.balance != total:
        raise ValueError(
            f"Wallet balance mismatch. Expected {total} got {wallet.balance}"
        )

