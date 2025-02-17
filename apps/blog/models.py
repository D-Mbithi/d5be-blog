from django.conf import settings
from django.db import models
from django.urls import reverse
from django.utils import timezone


class Status(models.TextChoices):
    DRAFT = "DF", "Draft"
    PUBLISHED = "PB", "Published"


class PublishedManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(status=Status.PUBLISHED)


class Post(models.Model):
    """Blog post model."""

    title = models.CharField(max_length=100)
    slug = models.SlugField(max_length=250, unique="publish")
    body = models.TextField()
    created_at = models.DateTimeField()
    updated = models.DateTimeField(auto_now=True)
    publish = models.DateTimeField(blank=True, null=True)
    category = models.ForeignKey(
        "Category", on_delete=models.CASCADE, related_name="posts"
    )
    status = models.CharField(
        max_length=2,
        choices=Status,
        default=Status.DRAFT,
    )
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="posts",
    )

    objects = models.Manager()
    published = PublishedManager()

    class Meta:
        ordering = ["-publish"]
        indexes = [
            models.Index(fields=["-publish"]),
        ]

    def __str__(self):
        return str(self.title)

    def get_absolute_url(self):
        return reverse("blog:post-detail", args=[self.id])

    def save(self, *args, **kwargs):
        if self.status == "PB" and self.publish is None:
            self.publish = timezone.now()
        super().save(*args, **kwargs)


class Category(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self) -> str:
        return str(self.name)

    def get_absolute_url(self):
        pass
