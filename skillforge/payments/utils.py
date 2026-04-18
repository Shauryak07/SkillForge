from payments.models import Wallet
from django.db import models

def total_system_money(self):
    balances = Wallet.objects.aggregate(total = models.Sum("balance"))["total"] or 0

    locked = Wallet.objects.aggregate(total = models.Sum("locked_balance"))["total"] or 0

    return balances + locked