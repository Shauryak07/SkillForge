from django.db import models
from users.models import CustomUser
from jobs.models import Job

# Create your models here.
class Bid(models.Model):

    class Status(models.TextChoices):
        PENDING = "pending"
        ACCEPTED = "accepted"
        REJECTED = "rejected"
        WITHDRAW = "withdraw"
        EXPIRED = "expired"

    job = models.ForeignKey(
        Job,
        on_delete=models.CASCADE,
        related_name="bids"
    )

    freelancer = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name="bids"
    )

    amount = models.DecimalField(max_digits=10, decimal_places=2)
    proposal = models.TextField()

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING
    )

    created_at = models.DateTimeField(auto_now_add=True)


    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["job","freelancer"],
                name="unique_bid_per_job_per_freelancer"
            )
        ]
        indexes = [
            models.Index(fields=["job","status"]),
            models.Index(fields=["freelancer"]),
        ]
