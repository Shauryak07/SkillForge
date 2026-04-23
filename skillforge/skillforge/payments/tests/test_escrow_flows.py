from django.test import TestCase
from decimal import Decimal
from users.models import CustomUser
from payments.models import Wallet, Transaction,PlatformSetting, TransactionType
from contracts.models import Contract
from payments.services import *
from contracts.workflows import approve_work
import threading
from django.test import TransactionTestCase
from django.db import connection, models

class EscrowFlowTests(TestCase):

    def setUp(self):
        #Users
        self.client = CustomUser.objects.create_user(
            username="client",
            email="client@test.com",
            password="pass"
        )

        self.freelancer = CustomUser.objects.create_user(
            username="freelancer",
            email="freelancer@test.com",
            password="pass"
        )

        self.system_user = CustomUser.objects.create_user(
            username="system",
            email="system@test.com",
            password="pass",
            is_system=True
        )


        # # Wallets
        # self.client_wallet = Wallet.objects.create(user=self.client, balance=Decimal("1000.00"))
        # self.freelancer_wallet = Wallet.objects.create(user=self.freelancer)
        # self.system_user = Wallet.objects.create(user=self.system_user)


        # # Job
        # self.job = Job.objects.create(
        #     title="Test Job",
        #     description="Test description",
        #     client=self.client
        # )

        # Platform fee 
        PlatformSetting.objects.create(commission_percentage=Decimal("10.00"))


        # Contract
        self.contract = Contract.objects.create(
            client = self.client,
            freelancer=self.freelancer,
            amount=Decimal("500.00")
        )

        # Wallets
        self.client_wallet = Wallet.objects.get(user=self.contract.client)
        self.client_wallet.balance = Decimal("1000.00")
        self.client_wallet.save()

    # Helper Functions
    def total_system_money(self):
        balances = Wallet.objects.aggregate(
            total = models.Sum("balance")
        )["total"] or 0

        locked = Wallet.objects.aggregate(
            total = models.Sum("locked_balance")
        )["total"] or 0

        return balances + locked

    # FUND CONTRACT TEST 
    def test_fund_contract_locks_money(self):
        fund_contract(self.contract)
        self.client_wallet.refresh_from_db()

        self.assertEqual(self.client_wallet.balance, Decimal("500.00"))
        self.assertEqual(self.client_wallet.locked_balance, Decimal("500.00"))
        self.assertEqual(Transaction.objects.count(), 1)


    # RELEASE ESCROW TEST
    def test_release_escrow_transfers_money_with_fee(self):
        fund_contract(self.contract)
        self.contract.status = "APPROVED"
        self.contract.save()
        release_escrow(self.contract)

        self.client_wallet.refresh_from_db()
        self.freelancer.wallet.refresh_from_db()
        self.system_user.wallet.refresh_from_db()

        # 10% fee = 50
        self.assertEqual(self.client_wallet.locked_balance, Decimal("0.00"))
        self.assertEqual(self.freelancer.wallet.balance, Decimal("450.00"))
        self.assertEqual(self.system_user.wallet.balance, Decimal("50.00"))


    # REFUND ESCROW TEST
    def test_refund_escrow_returns_money_to_client(self):
        fund_contract(self.contract)
        refund_escrow(self.contract)

        self.client.wallet.refresh_from_db()

        self.assertEqual(self.client_wallet.balance, Decimal("1000.00"))
        self.assertEqual(self.client_wallet.locked_balance, Decimal("0.00"))



    # IDEMPOTENCY TEST
    def test_fund_contract_is_idempotency(self):
        fund_contract(self.contract)
        with self.assertRaises(ValidationError):
            fund_contract(self.contract) # double calling

        self.client_wallet.refresh_from_db()

        self.assertEqual(self.client_wallet.locked_balance, Decimal("500.00"))
        self.assertEqual(Transaction.objects.count(), 1)

    def test_release_without_funding(self):

        with self.assertRaises(ValidationError):
            release_escrow(self.contract)

    def test_release_is_idempotent(self):
        fund_contract(self.contract)
        self.contract.status = "APPROVED"
        self.contract.save()
        release_escrow(self.contract)
        with self.assertRaises(ValidationError):
            release_escrow(self.contract)

        self.freelancer.wallet.refresh_from_db()
        self.system_user.wallet.refresh_from_db()

        self.assertEqual(self.freelancer.wallet.balance, Decimal("450.00"))
        self.assertEqual(self.system_user.wallet.balance, Decimal("50.00"))
        self.assertEqual(Transaction.objects.count(), 3)
            
    def test_for_double_funding_contract(self):
        fund_contract(self.contract)

        self.client_wallet.refresh_from_db()

        with self.assertRaises(ValidationError):
            fund_contract(self.contract)

        self.client_wallet.refresh_from_db()

        self.assertEqual(self.client_wallet.balance, 1000-self.contract.amount)
        self.assertEqual(self.client_wallet.locked_balance,self.contract.amount)


    def test_release_escrow_does_not_create_money(self):

        before = self.total_system_money()

        fund_contract(self.contract)
        self.contract.status = "APPROVED"
        self.contract.save()
        release_escrow(self.contract)

        after = self.total_system_money()

        assert before == after