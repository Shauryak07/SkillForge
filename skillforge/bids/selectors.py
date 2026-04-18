from bids.models import Bid
from jobs.models import Job

def get_job_bids(job):
    return Bid.objects.filter(job=job)

def get_job_with_bids(bid):
    return Job.objects.prefetch_related("bids").get(id=bid.id)

def get_pending_job_bids(job):
    return Bid.objects.filter(
        job=job,
        status=Bid.Status.PENDING
    )

def get_freelancer_active_bids(user):
    return Bid.objects.filter(freelancer=user,status=Bid.Status.PENDING)

