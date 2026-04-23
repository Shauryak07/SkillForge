from django.db import models
from users.models import CustomUser
from jobs.models import Job
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
        SPLIT_PAY = "SPLIT_PAY"   

    status = models.CharField(
        max_length = 20,
        choices=Status.choices,
        default=Status.DRAFT,
        db_index=True
    )

    current_submission = models.ForeignKey(
        "submissions.Submission",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+"
    )
    max_revisions = models.PositiveIntegerField(default=3)

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
    Contract.Status.SPLIT_PAY: set(),
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
        ESCROW_SPLIT = "escrow_split"

        DISPUTE_REQUESTED = "dispute_requested"
        DISPUTE_REQUEST_APPROVED = "dispute_request_approved"
        DISPUTE_REQUEST_REJECTED = "dispute_request_rejected"
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
