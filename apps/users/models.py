from django.contrib.auth.models import AbstractUser
from django.db import models


class Customuser(AbstractUser):
    """Custom user model defination"""

    email = models.EmailField(max_length=254, unique=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["first_name", "last_name"]

    def __str__(self):
        return str(self.email)
