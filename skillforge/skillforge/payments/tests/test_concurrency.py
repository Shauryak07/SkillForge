from django.core.exceptions import ValidationError
from contracts.models import Contract
from payments.services import release_escrow,fund_contract
from payments.models import Wallet,PlatformSetting,Transaction,TransactionType
from users.models import CustomUser
from decimal import Decimal
import threading
from django.test import TransactionTestCase
from django.db import connection

class ConcurrencyTest(TransactionTestCase):

    reset_sequences = True

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

        PlatformSetting.objects.create(commission_percentage=Decimal("10.00"))

        self.contract= Contract.objects.create(
            client= self.client,
            freelancer=self.freelancer,
            amount=Decimal("1000.00")
        )
        
        self.client_wallet = Wallet.objects.get(user=self.contract.client)
        self.client_wallet.balance = Decimal("1000.00")
        self.client_wallet.save()

    def test_concurrent_releases(self):
        fund_contract(self.contract)
        self.contract.status = "APPROVED"
        self.contract.save()
        def release():
            try:
                release_escrow(self.contract)
            except ValidationError:
                pass
            finally:
                connection.close()
            
        t1 = threading.Thread(target=release)
        t2 = threading.Thread(target=release)

        t1.start()
        t2.start()
        
        t1.join()
        t2.join()
        
        
        self.assertEqual(
            Transaction.objects.filter(
                contract=self.contract,
                transaction_type=TransactionType.DEPOSIT
            ).count()
            ,1
        )

    def test_balance_consistency_after_release(self):
        fund_contract(self.contract)
        self.contract.status = "APPROVED"
        self.contract.save()
        release_escrow(self.contract)

        self.client_wallet.refresh_from_db()
        self.freelancer.wallet.refresh_from_db()

        self.assertEqual(self.client_wallet.locked_balance,0)
        self.assertGreater(self.freelancer.wallet.balance, 0)

    def test_illegal_transition(self):

        with self.assertRaises(ValidationError):
            self.contract.transition_to(Contract.Status.PAID)