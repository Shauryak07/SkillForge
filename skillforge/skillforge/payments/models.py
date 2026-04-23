from django.db import models
import uuid

# Create your models here.
class Wallet(models.Model):
    user =  models.OneToOneField("users.CustomUser",on_delete=models.CASCADE, related_name="wallet")
    balance = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    locked_balance = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    def __str__(self):
        return f"{self.user.username} Wallet"


class Transaction(models.Model):
    wallet = models.ForeignKey(Wallet,on_delete=models.CASCADE,related_name="transactions")
    contract = models.ForeignKey(
        "contracts.Contract",
        null=True,
        blank=True,
        on_delete=models.SET_NULL
    )
    amount = models.DecimalField(max_digits=12,decimal_places=2)

    class TransactionType(models.TextChoices):
        DEPOSIT = "deposit", "Deposit"

        ESCROW_FUNDED = "escrow_funded", "Escrow_funded"
        ESCROW_RELEASED = "escrow_released", "Escrow_released"

        REFUND = "refund", "Refund"

        PLATFORM_FEE = "platform_fee", "Platform_fee"

    transaction_type = models.CharField(
        max_length=50,
        choices=TransactionType.choices
    )

    class TransactionDirection(models.TextChoices):
        CREDIT = "credit", "Credit"
        DEBIT = "debit", "Debit"
    

    transaction_direction = models.CharField(
        max_length=50,
        choices=TransactionType.choices
    )

    class ReferenceType(models.TextChoices):
        CONTRACT = "contract", "Contract"
        DISPUTE = "dispute", "Dispute"
        WALLET_TOPUP = "wallet_topup", "Wallet_topup"

    reference_type = models.CharField(
        max_length=50,
        choices=ReferenceType.choices,
        null=True,
        blank=True
    )

    reference_id = models.CharField(
        max_length=100,
        null=True,
        blank=True
    )

    balance_after = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0
    )
    reference = models.UUIDField(
        default=uuid.uuid4,
        editable=False,
        unique=True
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

class OperationLog(models.Model):
    status = models.CharField(max_length=20, choices=[
        ("STARTED", "STARTED"),
        ("SUCCESS", "SUCCESS"),
        ("FAILED", "FAILED"),
    ], default="STARTED")

    operation_key = models.CharField(max_length=250,unique=True)
    contract = models.ForeignKey("contracts.Contract",on_delete=models.CASCADE)
    actor = models.ForeignKey("users.CustomUser",on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class PlatformSetting(models.Model):
    commission_percentage = models.DecimalField(max_digits=5,decimal_places=2,default=10.00)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Commission: {self.commission_percentage}%"
    
    def save(self, *args, **kwargs):
        if not self.pk and PlatformSetting.objects.exists():
            raise ValueError("Only one PlatformSetting instance allowed")
        super().save(*args, **kwargs)
