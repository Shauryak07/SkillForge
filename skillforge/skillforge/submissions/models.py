from django.db import models
from users.models import CustomUser

# Create your models here.

class Submission(models.Model):

    class SubmissionStatus(models.TextChoices):
        PENDING = "pending"
        APPROVED = "approved"
        REJECTED = "rejected"

    contract = models.ForeignKey(
        "contracts.Contract",
        on_delete=models.CASCADE,
        related_name="submissions"
    )

    submitted_by = models.ForeignKey(
        CustomUser,
        on_delete=models.PROTECT,
        related_name="submissions"
    )

    reviewed_by = models.ForeignKey(
        CustomUser,
        on_delete=models.PROTECT,
        related_name="reviewed_submissions",
        null=True,
        blank=True
    )

    message = models.TextField(blank=True,null=True)
    feedback = models.TextField(blank=True,null=True)
    file = models.FileField(upload_to='uploads/',null=True)
    revision_number = models.PositiveIntegerField()
    status = models.CharField(max_length=20,choices=SubmissionStatus.choices,default=SubmissionStatus.PENDING)
    created_at = models.DateTimeField(auto_now_add=True)
    reviewed_at = models.DateTimeField(null=True,blank=True)

    class Meta:
        ordering = ["-created_at"]
        indexes  = [
            models.Index(fields=["contract","revision_number"]),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=["contract","revision_number"],
                name="unique_revision_per_contract"
            )
        ]