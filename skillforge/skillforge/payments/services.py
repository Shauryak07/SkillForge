from contracts.models import Contract, ContractEvent
from users.models import CustomUser
from django.db import transaction
from domain.invariants import (validate_wallet,validate_locked_balance,
                               validate_wallet_balance,
                               validate_wallet_transaction_consistency)
from payments.events import trigger_pay_event
from payments.models import (PlatformSetting, Transaction,
                            Wallet)
from payments.permissions import *
from payments.operation_engine import execute_operation
from decimal import Decimal
from disputes.helpers import ensure_no_active_disputes


def fund_contract(contract_id, client_id):
    operation_key = f"fund_contract:{contract_id}"

    contract = Contract.objects.select_for_update().get(id=contract_id)
    client = CustomUser.objects.select_for_update().get(id=client_id)

    def logic():
        can_fund_contract(client, contract)
        ensure_no_active_disputes(contract)
        
        client_wallet = Wallet.objects.select_for_update().get(user=contract.client)

        amount = contract.amount
        if client_wallet.balance < amount:
            raise ValueError(f"Insufficient Balance {client_wallet.balance}")

        # Update Wallet
        client_wallet.balance -= amount
        client_wallet.locked_balance += amount
        client_wallet.save(update_fields=["balance","locked_balance"])

        validate_wallet(client_wallet)
        validate_wallet_transaction_consistency(client_wallet)

        Transaction.objects.create(
            wallet=client_wallet,
            contract=contract,
            amount=contract.amount,
            transaction_type=TransactionType.ESCROW_LOCK,
            balance_after=client_wallet.balance,
        )

        contract.transition_to(Contract.Status.FUNDED)

        transaction.on_commit(
            trigger_pay_event(
                contract=contract,
                actor=client,
                event_type=ContractEvent.ContractEventType.CONTRACT_FUNDED
            )
        )
        
        return contract
    return execute_operation(operation_key,contract,client,logic)
    

def release_escrow(contract_id,client_id):
    operation_key = f"release_escrow:{contract_id}"

    contract = Contract.objects.select_for_update().get(id=contract_id)
    client = CustomUser.objects.select_for_update().get(id=client_id)

    def logic():
        ensure_no_active_disputes(contract)
        can_release_escrow(client,contract)

        # Wallets
        wallets = list(
            Wallet.objects.select_for_update()
            .filter(user__in=[contract.client,contract.freelancer]) |
            Wallet.objects.filter(user__is_system=True)
        )

        client_wallet = next((w for w in wallets if w.user_id == contract.client_id),None)
        freelancer_wallet = next(w for w in wallets if w.user_id == contract.freelancer_id)

        platform_wallet = next(w for w in wallets if w.user.is_system)

        # Balance Check
        amount = contract.amount
        if client_wallet.locked_balance < amount:
            raise ValueError("Insufficient Locked Balance")

        # Commision
        commission_percentage = PlatformSetting.objects.first().commission_percentage
        fee = (amount * Decimal(commission_percentage))/Decimal("100")
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

    
        Transaction.objects.create(
            wallet=freelancer_wallet,
            contract=contract,
            amount=freelancer_amount,
            transaction_type=TransactionType.DEPOSIT,
            balance_after=freelancer_wallet.balance,
        )

        Transaction.objects.create(
            wallet=platform_wallet,
            contract=contract,
            amount = fee,
            transaction_type = TransactionType.PLATFORM_FEE,
            balance_after = platform_wallet.balance,
        )

        contract.transition_to(Contract.Status.PAID)

        transaction.on_commit(
            trigger_pay_event(
                contract=contract,
                actor=client,
                event_type=ContractEvent.ContractEventType.ESCROW_RELEASED
            )
        )
        return contract
    return execute_operation(operation_key,contract,client,logic)


""" Internal Function """
def refund_escrow(contract_id,actor_id):
    operation_key = f"refund_escrow:{contract_id}"

    contract = Contract.objects.select_for_update().get(id=contract_id)
    actor = CustomUser.objects.get(id=actor_id)

    def logic():
        can_refund_escrow(contract)
        """
        Think about it and change it when free
        """

        client_wallet = Wallet.objects.select_for_update().get(user=contract.client)

        # Balance Check
        amount = contract.amount
        validate_locked_balance(client_wallet.locked_balance,amount)

        # Update Wallet
        client_wallet.locked_balance -= amount
        client_wallet.balance += amount
        client_wallet.save(update_fields=["locked_balance","balance"])

        validate_wallet(client_wallet)
        validate_wallet_transaction_consistency(client_wallet)

        Transaction.objects.create(
            wallet=client_wallet,
            contract=contract,
            amount=amount,
            transaction_type = TransactionType.REFUND,
            balance_after=client_wallet.balance
        )
        
        contract.transition_to(Contract.Status.REFUNDED)

        transaction.on_commit(
            trigger_pay_event(
                contract=contract,
                actor=actor,
                event_type=ContractEvent.ContractEventType.ESCROW_REFUNDED
            )
        )
        
        return contract
    
    return execute_operation(operation_key,contract,actor,logic)

"""Internal Function"""
def split_escrow(contract_id,actor_id,client_split_percent,freelancer_split_percent):
    contract = Contract.objects.select_for_update().get(id = contract_id)
    actor = CustomUser.objects.get(id=actor_id)
    operation_key = f"split_escrow:{contract.id}"

    def logic():
        can_split_escrow(contract)

        wallets = list(
            Wallet.objects.select_for_update().
            filter(user__in=[contract.client,contract.freelancer])
        )

        client_wallet = next((w for w in wallets if w.user_id==contract.client_id),None)
        freelancer_wallet = next((w for w in wallets if w.user_id==contract.freelancer_id),None)
        
        validate_locked_balance(client_wallet.locked_balance,contract.amount)

        client_split_amount = (client_split_percent / 100) * contract.amount
        freelancer_split_amount = (freelancer_split_percent / 100) * contract.amount

        client_wallet.locked_balance -= client_split_amount
        client_wallet.balance += client_split_amount

        client_wallet.locked_balance -= freelancer_split_amount
        freelancer_wallet.balance += freelancer_split_amount

        client_wallet.save()
        freelancer_wallet.save()

        validate_wallet(client_wallet)

        """Write a similar function for split escrow"""
        # validate_wallet_transaction_consistency(client_wallet)

        Transaction.objects.create()

        Transaction.objects.create(
            wallet=freelancer_wallet,
            contract=contract,
            amount=freelancer_split_amount,
            transaction_type=Transaction.TransactionType.ESCROW_RELEASED,
            transaction_direction  = Transaction.TransactionDirection.CREDIT,
            reference_type = Transaction.ReferenceType.DISPUTE,
            reference_id = contract.dispute_id,
            balance_after=freelancer_wallet.balance,
        )

        Transaction.objects.create(
            wallet=client_wallet,
            contract=contract,
            amount = client_split_amount,
            transaction_type=Transaction.TransactionType.REFUND,
            transaction_direction  = Transaction.TransactionDirection.CREDIT,
            reference_type = Transaction.ReferenceType.DISPUTE,
            reference_id = contract.dispute_id,
            balance_after = client_wallet.balance,
        )

        contract.transition_to(Contract.Status.SPLIT_PAY)

        transaction.on_commit(
            trigger_pay_event(
                contract=contract,
                actor=actor,
                event_type=ContractEvent.ContractEventType.ESCROW_SPLIT
            )
        )

        return contract

    return execute_operation(operation_key,contract,actor,logic)


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
    

