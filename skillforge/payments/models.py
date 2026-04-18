from django.db import models
from users.models import CustomUser
from django.db import transaction
from decimal import Decimal
import uuid

# Create your models here.
class Wallet(models.Model):
    user =  models.OneToOneField(CustomUser,on_delete=models.CASCADE, related_name="wallet")
    balance = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    locked_balance = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    def __str__(self):
        return f"{self.user.username} Wallet"

class TransactionType(models.TextChoices):
    DEPOSIT = "deposit", "Deposit"
    ESCROW_LOCK = "escrow_lock", "Escrow_lock"
    ESCROW_RELEASE = "escrow_release", "Escrow_release"
    REFUND = "refund", "Refund"
    PLATFORM_FEE = "platform_fee", "Platform_fee"

class Transaction(models.Model):
    wallet = models.ForeignKey(Wallet,on_delete=models.CASCADE,related_name="transactions")
    contract = models.ForeignKey(
        "contracts.Contract",
        null=True,
        blank=True,
        on_delete=models.SET_NULL
    )
    amount = models.DecimalField(max_digits=12,decimal_places=2)
    transaction_type = models.CharField(
        max_length=50,
        choices=TransactionType.choices
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

    operation_key = models.CharField(
        max_length=250,
        unique=True,
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

class PlatformSetting(models.Model):
    commission_percentage = models.DecimalField(max_digits=5,decimal_places=2,default=10.00)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Commission: {self.commission_percentage}%"
    
    def save(self, *args, **kwargs):
        if not self.pk and PlatformSetting.objects.exists():
            raise ValueError("Only one PlatformSetting instance allowed")
        super().save(*args, **kwargs)
