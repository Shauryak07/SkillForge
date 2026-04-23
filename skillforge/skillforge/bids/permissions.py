from django.core.exceptions import ValidationError
from jobs.models import Job
from bids.models import Bid

def can_accept_bid(bid, actor):

    if bid.job.client != actor:
        raise ValidationError(
            f"Only job owner can accept bids"
        )

    if bid.status != Bid.Status.PENDING:
        raise ValidationError(
            f"Bid is not Pending"
        )

def can_reject_bid(bid, actor):

    if bid.job.client != actor:
        raise ValidationError(
            f"Only job owner can accept bids"
        )

    if bid.status != Bid.Status.PENDING:
        raise ValidationError(
            f"Bid is not Pending"
        )


def can_withdraw_bid(bid, actor):

    if bid.job.client != actor:
        raise ValidationError(
            f"Only bidder can withdraw bid"
        )

    if bid.status != Bid.Status.PENDING:
        raise ValidationError(
            f"Cannot withdraw processed bid"
        )

def can_place_bid(actor, job):

    if job.client == actor:
        raise ValidationError(
            f"Client cannot bid on own job"
        )
    
    if job.status != Job.Status.OPEN:
        raise ValidationError(
            f"Cannot bid on a closed job"
        )

def can_update_bid(actor, bid):

    if bid.freelancer != actor:
        raise ValidationError(
            f"Cannot edit someone else's bid"
        )
    
    if bid.status != Bid.Status.PENDING:
        raise ValidationError(
            f"Cannot edit processed bid"
        )