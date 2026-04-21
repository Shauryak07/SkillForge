from django.db import transaction,IntegrityError
from payments.models import Transaction, PlatformSetting, TransactionType
from payments.models import Wallet
from django.utils.crypto import get_random_string
from contracts.models import Contract, ContractEvent
from django.core.exceptions import ValidationError
from contracts.permissions import *
from payments.events import trigger_pay_event
from domain.invariants import validate_wallet, validate_wallet_transaction_consistency

@transaction.atomic
def fund_contract(contract, actor):
    can_fund_contract(actor=actor, contract=contract)
    contract = Contract.objects.select_for_update().get(id=contract.id)
    wallet = Wallet.objects.select_for_update().get(user=contract.client)
    # ensure_no_active_disputes(contract)
        
    # Status Check
    operation_key = f"fund_contract_{contract.id}"
    
    # Balance Check
    amount = contract.amount
    if wallet.balance < amount:
        raise ValueError(f"Insufficient Balance {wallet.balance}")

    # Update Wallet
    wallet.balance -= amount
    wallet.locked_balance += amount
    wallet.save(update_fields=["balance","locked_balance"])

    validate_wallet(wallet)
    validate_wallet_transaction_consistency(wallet)

    try:
        Transaction.objects.create(
            wallet=wallet,
            contract=contract,
            amount=contract.amount,
            transaction_type=TransactionType.ESCROW_LOCK,
            balance_after=wallet.balance,
            operation_key=operation_key
        )
    except IntegrityError:
        return

    # Change Contract Status
    contract.transition_to(Contract.Status.FUNDED)

    transaction.on_commit(trigger_pay_event(contract,actor,ContractEvent.ContractEventType.CONTRACT_FUNDED))

    return contract
    
@transaction.atomic
def release_escrow(contract, actor):
    # Status Check
    contract = Contract.objects.select_for_update().get(id=contract.id)
    ensure_no_active_disputes(contract)
    can_release_escrow(actor,contract)

    base_key = f"release_{contract.id}"

    # Wallets
    client_wallet = Wallet.objects.select_for_update().get(user=contract.client)
    freelancer_wallet = Wallet.objects.select_for_update().get(user=contract.freelancer)
    platform_wallet = Wallet.objects.select_for_update().get(user__is_system=True)

    # Balance Check
    amount = contract.amount
    if client_wallet.locked_balance < amount:
        raise ValueError("Insufficient Locked Balance")

    # Commision
    commission_percentage = PlatformSetting.objects.first().commission_percentage
    fee = (amount * commission_percentage)/100
    freelancer_amount = amount - fee
    
    # Wallet Update
    client_wallet.locked_balance -= amount
    freelancer_wallet.balance += freelancer_amount
    platform_wallet.balance += fee

    client_wallet.save(update_fields=["locked_balance"])
    freelancer_wallet.save(update_fields=["balance"])
    platform_wallet.save(update_fields=["balance"])

    validate_wallet(client_wallet)
    validate_wallet(freelancer_wallet)
    validate_wallet_transaction_consistency(client_wallet)
    validate_wallet_transaction_consistency(freelancer_wallet)

    try:
        Transaction.objects.create(
            wallet=freelancer_wallet,
            contract=contract,
            amount=freelancer_amount,
            transaction_type=TransactionType.DEPOSIT,
            balance_after=freelancer_wallet.balance,
            operation_key=f"{base_key}_freelancer"
        )

        Transaction.objects.create(
            wallet=platform_wallet,
            contract=contract,
            amount = fee,
            transaction_type = TransactionType.PLATFORM_FEE,
            balance_after = platform_wallet.balance,
            operation_key=f"{base_key}_platform"
        )
    except IntegrityError:
        return
    
    # Change Contract Status
    contract.transition_to(Contract.Status.PAID)
    transaction.on_commit(trigger_pay_event(contract,actor,ContractEvent.ContractEventType.ESCROW_RELEASED))

@transaction.atomic
def refund_escrow(contract):
    operation_key = f"refund_{contract.id}"
    contract = Contract.objects.select_for_update().get(id=contract.id)
    ensure_no_active_disputes(contract)
    can_refund_escrow(contract)
    
    """
    Think about it and change it when free
    """

    # Status Check 
    if contract.status not in [Contract.Status.FUNDED, Contract.Status.IN_PROGRESS]:
        raise ValidationError(f"Cannot refund from the state {contract.status}")

    # Balance Check
    client_wallet = Wallet.objects.select_for_update().get(user=contract.client)
    amount = contract.amount
    if wallet.locked_balance < amount:
        raise ValueError("Insufficient Locked Balance")

    # Update Wallet
    client_wallet.locked_balance -= amount
    client_wallet.balance += amount
    client_wallet.save(update_fields=["locked_balance","balance"])

    validate_wallet(client_wallet)
    validate_wallet_transaction_consistency(client_wallet)

    try:
        Transaction.objects.create(
            wallet=client_wallet,
            contract=contract,
            amount=amount,
            transaction_type = TransactionType.REFUND,
            balance_after=client_wallet.balance,
            operation_key=operation_key
        )
    except IntegrityError:
        return

    # Change Contract Status
    contract.transition_to(Contract.Status.REFUNDED)
    transaction.on_commit(trigger_pay_event(contract,actor,ContractEvent.ContractEventType.ESCROW_REFUNDED))

# @transaction.atomic
# def lock_funds(contract):
#     operation_key = f"lock_funds_{contract.id}"
#     """Adds funds into client's locked balance if balance is sufficient"""
#     client_wallet = contract.client_wallet
    
#     client_wallet = (
#         Wallet.objects.select_for_update().get(user=contract.client)
#     )

#     if client_wallet.balance < amount : 
#         raise ValueError("Insufficient balance")

#     # Update balances 
#     client_wallet.balance = F('balance') - amount
#     client_wallet.locked_balance = F('locked_balance') + amount
#     client_wallet.save(update_fields=["balance","locked_balance"])

#     client_wallet.refresh_from_db()

#     try:
#         Transaction.objects.create(
#             wallet=wallet,
#             contract=contract,
#             amount=amount,
#             transaction_type = TransactionType.DEPOSIT,
#             balance_after=wallet.balance,
#             operation_key=operation_key
#         )
#     except IntegrityError:
#         return
    

