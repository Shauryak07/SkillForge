from django.contrib import admin
from payments.models import Wallet,Transaction,PlatformSetting

# Register your models here.
admin.site.register(Wallet)
admin.site.register(Transaction)
admin.site.register(PlatformSetting)