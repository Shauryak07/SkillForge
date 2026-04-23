from django.db import models
from django.utils import timezone
from django.db.models import Q

# Create your models here.
class Dispute(models.Model):

    class Status(models.TextChoices):
        OPEN = "OPEN"
        RESOLVED = "RESOLVED"

    class Resolution(models.TextChoices):
        CLIENT = "CLIENT"
        FREELANCER = "FREELANCER"
        SPLIT = "SPLIT"

    contract = models.ForeignKey(
        "contracts.Contract",
        on_delete=models.CASCADE,
        related_name="dispute"
    )

    opened_by = models.ForeignKey(
        "users.CustomUser",
        on_delete = models.PROTECT,
        related_name="opened_disputes"
    )

    resolved_by = models.ForeignKey(
        "users.CustomUser",
        on_delete=models.PROTECT,
        blank=True,
        null=True,
        related_name="resolved_disputes"
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

    operation_key = models.CharField(max_length=255, null=True, blank=True)

    client_amount_percentage = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True
    )
    freelancer_amount_percentage = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True
    )


    created_at = models.DateTimeField(auto_now_add=True)
    resolved_at = models.DateTimeField()

    class Meta:
        indexes = [
            models.Index(fields=['contract','status'])
        ]
        constraints = [
        models.UniqueConstraint(
            fields=['contract'],
            condition=Q(status='OPEN'),
            name='unique_open_dispute_per_contract'
        )
    ]

    def __str__(self):
        return f"Dispute {self.id} raised by {self.opened_by} on {self.created_at}"
    
    def is_open(self):
        return self.status == self.Status.OPEN
    
    def mark_resolved(self,actor,resolution, client_amount=None, freelancer_amount=None):
        if self.status != self.Status.OPEN:
            raise ValueError("Dispute already resolved")
        
        self.status = self.Status.RESOLVED
        self.resolution = resolution
        self.resolved_by = actor
        self.resolved_at = timezone.now()

        if resolution == self.Resolution.SPLIT:
            if client_amount is None or freelancer_amount is None:
                raise ValueError("Split requires both amounts")

            total = client_amount + freelancer_amount
            if total <= 0:
                raise ValueError("Invalid split amounts")
            
            self.client_amount = client_amount
            self.freelancer_amount = freelancer_amount

        self.save()