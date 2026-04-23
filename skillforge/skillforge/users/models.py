from django.db import models
from django.contrib.auth.models import AbstractUser
from users.manager import UserManager

# Create your models here.
class CustomUser(AbstractUser):

    first_name = None
    last_name = None
    email = models.EmailField(unique=True)
    user_bio = models.CharField(max_length=50, blank=True)

    is_system = models.BooleanField(default=False)

    REQUIRED_FIELDS = ['email']
    objects = UserManager()

    def __str__(self):
        return self.username