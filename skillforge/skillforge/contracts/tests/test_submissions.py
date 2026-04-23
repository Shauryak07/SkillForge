from django.test import TestCase
from users.models import CustomUser
from contracts.models import Contract, ContractEvent, Submission
from payments.models import Wallet
from jobs.models import Job
from bids.services import *
from jobs.services import *
from contracts.workflows import *
from decimal import Decimal
from payments.services import *

# Create your tests here.

class SubmissionTest(TestCase):

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

        # Contract
        self.contract = Contract.objects.create(
            client = self.client,
            freelancer=self.freelancer,
            amount=Decimal("500.00")
        )

        # Wallets
        self.client_wallet = Wallet.objects.get(user=self.contract.client)
        self.client_wallet.balance = Decimal("3000.00")
        self.client_wallet.save()

        self.job = Job.objects.create(
            title="test job",
            description="test",
            client=self.client,
            budget=1000,
        )

    def test_submission(self):
        self.job.status = Job.Status.OPEN
        self.job.save()

        place_bid(
            job=self.job,
            actor=self.freelancer,
            amount=800,
            proposal="this is a test proposal"
        )
        
        bid = Bid.objects.get(job=self.job)
        accept_bid(bid,self.client)
        self.contract = fund_contract(self.contract,self.contract.client)

        self.contract.transition_to(Contract.Status.IN_PROGRESS)

        submission = submit_work(self.contract,self.freelancer,"this is first submission")
        self.contract.refresh_from_db()

        self.assertEqual(submission.revision_number,1)
        self.assertEqual(self.contract.status,Contract.Status.SUBMITTED)
        
    def test_submission_client_rejects(self):
        self.job.status = Job.Status.OPEN
        self.job.save()

        place_bid(
            job=self.job,
            actor=self.freelancer,
            amount=800,
            proposal="this is a test proposal"
        )
        
        bid = Bid.objects.get(job=self.job)
        reject_bid(bid,self.client)
        
        self.contract.refresh_from_db()

        self.assertEqual(self.contract.status,Contract.Status.DRAFT)