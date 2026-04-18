from jobs.models import JobEvent
from jobs.models import JobEvent
from bids.models import Bid
from contracts.models import Contract
from jobs.handlers import *

def trigger_job_event(job,actor,event_type):
    JobEvent.objects.create(
        job=job,
        actor=actor,
        event_type=event_type
    )

    # JOBS

    if event_type == JobEvent.EventType.JOB_CREATED:
        pass

    if event_type == JobEvent.EventType.JOB_UPDATED:
        pass

    if event_type == JobEvent.EventType.JOB_CLOSED:
        pass


    # BIDS

    if event_type == JobEvent.EventType.BID_ACCEPTED:
        handle_accepted_bid()
        
    elif event_type == JobEvent.EventType.BID_PLACED:
        handle_placed_bid()

    elif event_type == JobEvent.EventType.BID_REJECTED:
        handle_rejected_bid()

    elif event_type == JobEvent.EventType.BID_UPDATED:
        handle_updated_bid()

    elif event_type == JobEvent.EventType.BID_WITHDREW:
        handle_withdrew_bid()