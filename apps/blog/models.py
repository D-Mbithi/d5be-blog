from django.conf import settings
from django.db import models
from django.utils import timezone


class Status(models.TextChoices):
    DRAFT = "DF", "Draft"
    PUBLISHED = "PB", "Published"


# Create your models here.
class Post(models.Model):
    """Blog post model."""

    title = models.CharField(max_length=100)
    slug = models.SlugField(max_length=250)
    body = models.TextField()
    created_at = models.DateTimeField()
    updated = models.DateTimeField(auto_now=True)
    publish = models.DateTimeField(blank=True, null=True)
    category = models.ForeignKey(
        "Category", on_delete=models.CASCADE, related_name="posts"
    )
    status = models.CharField(
        max_length=2,
        choices=Status.choices,
        default=Status.DRAFT,
    )
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="posts",
    )

    class Meta:
        ordering = ["-publish"]
        indexes = [
            models.Index(fields=["-publish"]),
        ]

    def __str__(self):
        return str(self.title)


class Category(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self) -> str:
        return str(self.name)
