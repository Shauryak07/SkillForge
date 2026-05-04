from bids.permissions import *
from bids.models import Bid
from django.db import transaction
from jobs.events import trigger_job_event
from jobs.models import JobEvent
from contracts.workflows import create_contract

@transaction.atomic
def accept_bid(bid, actor):
    bid = Bid.objects.select_related("job").get(id=bid.id)

    job = Job.objects.select_for_update().get(id=bid.job.id)

    can_accept_bid(bid,actor)

    if job.status != Job.Status.OPEN:
        raise ValidationError(
            f"Job already assigned"
        )
    
    contract = create_contract(job,job.client,bid.freelancer,bid.amount)

    job.status = Job.Status.IN_PROGRESS
    job.save(update_fields=["status"])

    bid.status = Bid.Status.ACCEPTED
    bid.save(update_fields=["status"])

    # Rejecting other bids
    Bid.objects.filter(
        job=job,
        status=Bid.Status.PENDING
    ).exclude(id=bid.id).update(
        status=Bid.Status.REJECTED
    )

    trigger_job_event(job,actor,JobEvent.EventType.BID_ACCEPTED)
    return bid


def reject_bid(bid, actor):
    can_reject_bid(bid, actor)

    bid.status = Bid.Status.REJECTED
    bid.save(update_fields=["status"])

    trigger_job_event(bid.job,actor,JobEvent.EventType.BID_REJECTED)


def place_bid(job, actor, amount, proposal):
    can_place_bid(job=job, actor=actor)

    bid = Bid.objects.create(
        job=job,
        freelancer= actor,
        amount=amount, 
        proposal=proposal
    )

    trigger_job_event(bid.job,actor,JobEvent.EventType.BID_PLACED)

    return bid

def withdraw_bid(bid, actor):
    bid = Bid.objects.select_for_update().get(id=bid.id)
    can_withdraw_bid(bid, actor)

    bid.status = Bid.Status.WITHDRAW
    bid.save(update_fields=["status"])

    trigger_job_event(bid.job,actor,JobEvent.EventType.BID_WITHDREW)

def update_bid(bid, actor, amount, proposal):
    can_update_bid(actor, bid)

    bid.amount = amount
    bid.proposal = proposal
    bid.save(update_bid=["amount","proposal"])

    trigger_job_event(bid.job,actor,JobEvent.EventType.BID_UPDATED)