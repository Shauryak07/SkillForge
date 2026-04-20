from django.db import models
from users.models import CustomUser
from jobs.models import Job
from bids.models import Bid
from django.conf import settings
from django.core.exceptions import ValidationError

# Create your models here.

class Contract(models.Model):
    job = models.OneToOneField(
        Job,
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )

    client = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name="client_contracts"
    )

    freelancer = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name="freelancer_contracts"
    )

    amount = models.DecimalField(
        max_digits=12,
        decimal_places=2
    )

    class Status(models.TextChoices):
        DRAFT = "DRAFT"
        FUNDED = "FUNDED"
        IN_PROGRESS = "IN_PROGRESS"
        SUBMITTED = "SUBMITTED"
        APPROVED = "APPROVED"
        PAID = "PAID"
        REFUNDED = "REFUNDED"
        CANCELLED = "CANCELLED"
        DISPUTED = "DISPUTED"      

    status = models.CharField(
        max_length = 20,
        choices=Status.choices,
        default=Status.DRAFT,
        db_index=True
    )

    current_submission = models.ForeignKey(
        "Submission",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+"
    )

    def allowed_transition(self):
        return ALLOWED_TRANSITIONS.get(self.status, set())

    def transition_to(self, new_status):
        allowed = ALLOWED_TRANSITIONS.get(self.status, set())

        if new_status not in allowed:
            raise ValidationError(
                f"Illegal transition: {self.status} -> {new_status}"
            )
    
        self.status = new_status
        self.save(update_fields=["status"])

ALLOWED_TRANSITIONS = {
    Contract.Status.DRAFT: {Contract.Status.FUNDED, Contract.Status.CANCELLED},
    Contract.Status.FUNDED: {Contract.Status.IN_PROGRESS},
    Contract.Status.IN_PROGRESS : {Contract.Status.SUBMITTED,Contract.Status.REFUNDED},
    Contract.Status.SUBMITTED : {Contract.Status.APPROVED},
    Contract.Status.APPROVED : {Contract.Status.PAID},
    Contract.Status.PAID : set(),
    Contract.Status.REFUNDED : set(),
    Contract.Status.CANCELLED: set(),
    Contract.Status.DISPUTED: {Contract.Status.IN_PROGRESS,Contract.Status.REFUNDED,Contract.Status.PAID}
} 
# Audit Log
class ContractEvent(models.Model):
    contract = models.ForeignKey(
        Contract,
        on_delete=models.CASCADE,
        related_name="events"
    )

    actor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL
    )

    class ContractEventType(models.TextChoices):
        CONTRACT_CREATED = "contract_created"
        CONTRACT_CANCELLED = "contract_cancelled"
        CONTRACT_FUNDED = "contract_funded"
        CONTRACT_ACTIVATED = "contract_activated"

        WORK_SUBMITTED = "work_submitted"
        WORK_REJECTED = "work_rejected"
        WORK_APPROVED = "work_approved"
                               
        ESCROW_RELEASED = "escrow_released"
        ESCROW_REFUNDED = "escrow_refunded"

        DISPUTE_OPENED = "dispute_opened"
        DISPUTE_RESOLVED = "dispute_resolved"
        DISPUTE_CLOSED = "dispute_closed"

    event_type = models.CharField(max_length=50,choices=ContractEventType.choices)
    operation_key = models.CharField(
        max_length=250,
        unique=True,
    )

    EVENT_STATUS = [
        ("PENDING","pending"),
        ("PROCESSING","processing"),
        ("PROCESSED","processed"),
        ("FAILED","failed"),
    ]

    status = models.CharField(choices=EVENT_STATUS,max_length=20,default="PENDING")
    retry_count = models.IntegerField(default=0)

    processed_at  = models.DateTimeField(null=True,blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"[{self.actor}] {self.event_type} - {self.contract_id}" # contract_id is just same default id created by django 

class Submission(models.Model):

    class SubmissionStatus(models.TextChoices):
        SUBMITTED = "submitted"
        REJECTED = "rejected"
        APPROVED = "approved"

    contract = models.ForeignKey(
        Contract,
        on_delete=models.CASCADE,
        related_name="submissions"
    )

    submitted_by = models.ForeignKey(
        CustomUser,
        on_delete=models.PROTECT,
        related_name="submissions"
    )

    message = models.TextField()
    file = models.FileField(upload_to='uploads/',null=True)
    revision_number = models.PositiveIntegerField(default=0)
    status = models.CharField(max_length=20,choices=SubmissionStatus.choices,default=SubmissionStatus.SUBMITTED)
    created_at = models.DateTimeField(auto_now_add=True)

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

class Dispute(models.Model):

    class Status(models.TextChoices):
        OPEN = "OPEN"
        RESOLVED = "RESOLVED"
        CLOSED = "CLOSED"

    class Resolution(models.TextChoices):
        CLIENT = "CLIENT"
        FREELANCER = "FREELANCER"
        SPLIT = "SPLIT"

    contract = models.OneToOneField(
        Contract,
        on_delete=models.CASCADE,
        related_name="disputes"
    )

    opened_by = models.ForeignKey(
        CustomUser,
        on_delete = models.PROTECT,
        related_name="disputes"
    )

    reason = models.TextField()

    status = models.CharField(
        max_length=15,
        choices=Status.choices,
        default=Status.OPEN
    )

    resolution = models.CharField(
        max_length=10,
        choices=Resolution.choices,
        null=True,
        blank=True
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Dispute {self.id} raised by {self.opened_by} on {self.created_at}"

    