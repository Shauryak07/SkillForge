# When "something" happens do "this" automatically

from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver
from payments.models import Wallet

@receiver(post_save, sender=settings.AUTH_USER_MODEL) # if any model.save is used ex -> user.save
def create_wallet(sender, instance, created, **kwargs): 
    if created: # if any new user is created
        Wallet.objects.create(user=instance) # Creating wallet for the new user
        