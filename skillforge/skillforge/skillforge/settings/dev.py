# Development Settings

from .base import *
import os

DEBUG = True

ALLOWED_HOSTS = ["127.0.0.1","localhost"]

AUTHENTICATION_BACKENDS = [
    "users.backends.UsernameOrEmailBackend",
    "django.contrib.auth.backends.ModelBackend",
]

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.getenv("DB_NAME", "skillforge_db"),
        "USER": os.getenv("DB_USER", "skillforge_user"),
        "PASSWORD": os.getenv("DB_PASSWORD"),
        "HOST": os.getenv("DB_HOST", "localhost"),
        "PORT": os.getenv("DB_PORT", "5432"),
    }
}