from django.contrib.auth.models import AbstractUser
from django.db import models
from .managers import CustomUserManager
from model_utils.models import TimeStampedModel


class CustomUser(AbstractUser):
    """Custom user model."""

    username = None
    email = models.EmailField(max_length=254, unique=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    objects = CustomUserManager()

    def __str__(self):
        return str(self.email)

class Profile(TimeStampedModel):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name="profile")
    full_name = models.CharField(max_length=255, null=True, blank=True)
    bio = models.TextField(blank=True)
    image = models.ImageField(upload_to="profile_pics", blank=True)

    def __str__(self):
        return self.user.email
