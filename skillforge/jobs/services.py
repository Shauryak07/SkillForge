from jobs.models import Job, JobEvent
from jobs.permissions import *
from jobs.events import trigger_job_event

def create_job(title,description,client,budget,status):
    job = Job.objects.create(
        title=title,
        description=description,
        client=client,
        budget=budget,
    )
    trigger_job_event(job,actor,JobEvent.EventType.JOB_CREATED)
    return job

def cancel_job(actor,job):
    can_cancel_job(actor, job)

    job.status = Job.Status.CANCELLED
    job.save()

    trigger_job_event(job,actor,JobEvent.EventType.JOB_CLOSED)

def update_job(actor, job, title=None, description=None, budget=None):
    can_update_job(actor,job)

    if title:
        job.title = title
    if description:
        job.description = description
    if budget:
        job.budget = budget

    job.save()

    trigger_job_event(job,actor,JobEvent.EventType.JOB_UPDATED)

