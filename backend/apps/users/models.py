from django.contrib.auth.models import AbstractUser
from django.db.models.signals import post_save
from django.dispatch import receiver
from django_extensions.db.models import TimeStampedModel
from django.db import models
from django.conf import settings


class CustomUser(AbstractUser):
    pass

    def __str__(self):
        return self.get_username()



class Profile(TimeStampedModel):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='profile')
    bio = models.TextField(default='', blank=True)
    profile_pic = models.ImageField(upload_to='profile_pics', blank=True, default='profile_pics/default.jpg')

    def __str__(self):
        return self.user.email

    class Meta:
        verbose_name = "User Profile"
        verbose_name_plural = "User Profiles"



@receiver(post_save, sender=CustomUser, dispatch_uid="create_profile_object")
def create_profile_object(sender, instance, created, **kwargs):
    if created:
        if kwargs.get("raw"):
            return
        Profile.objects.get_or_create(user=instance)