from jobs.models import Job
from django.core.exceptions import ValidationError

def is_client(actor, job):
    return actor == job.client

def can_update_job(actor,job):
    if not is_client(actor,job):
        raise ValidationError(
            f"Only client can edit this job"
        )
    if job.status not in [Job.Status.DRAFT, Job.Status.OPEN]:
        raise ValidationError(
            f"You cannot perform such action in {job.status} state"
        )

def can_cancel_job(actor,job):
    if not is_client(actor,job):
        raise ValidationError(
            f"Only client can cancel this job"
        )

    if job.status not in [Job.Status.DRAFT, Job.Status.OPEN]:
        raise ValidationError(
            f"You cannot perfor"
        )