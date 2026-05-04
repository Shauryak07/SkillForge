from django.db import models
from users.models import CustomUser

# Create your models here
class Job(models.Model):

    class Status(models.TextChoices):
        DRAFT = "draft"
        OPEN = "open"
        IN_PROGRESS = "in_progress"
        COMPLETED = "completed"
        CANCELLED = "cancelled"


    title = models.CharField(max_length=200)
    description = models.TextField()
    

    # only created when user posts a job
    client = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name="posted_jobs"
    )

    budget = models.DecimalField(max_digits=12,decimal_places=2,default=0)
    status = models.CharField(max_length=20,choices=Status.choices,default=Status.DRAFT)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=["status"]),
            models.Index(fields=["created_at"]),
        ]

class JobEvent(models.Model):

    class EventType(models.TextChoices):
        JOB_CREATED = "job_created", "Job Created"
        JOB_UPDATED = "job_updated", "Job Updated"
        JOB_COMPLETED = "job_completed", "Job Completed"
        JOB_CLOSED = "job_closed", "Job Closed"
        BID_PLACED = "bid_placed", "Bid Placed"
        BID_ACCEPTED = "bid_accepted", "Bid Accepted"
        BID_REJECTED = "bid_rejected", "Bid Rejected"
        BID_WITHDREW = "bid_withdrew", "Bid Withdrew"
        BID_UPDATED = "bid_updated", "Bid Updated"


    job = models.ForeignKey(
        Job,
        on_delete=models.CASCADE,
        related_name="events"
    )

    actor = models.ForeignKey(
        CustomUser,
        null=True,
        on_delete=models.SET_NULL
    )

    event_type = models.CharField(max_length=50,choices=EventType.choices)

    created_at = models.DateTimeField(auto_now_add=True)