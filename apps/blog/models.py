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

    # def get_published(self):
    #     return self.get_queryset().filter(is_featured=True).order_by("-publish")


class Post(models.Model):
    """Blog post model."""

    title = models.CharField(max_length=100)
    slug = models.SlugField(max_length=250, unique_for_date="publish")
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
    is_featured = models.BooleanField(default=False)

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
        return reverse(
            "blog:post-detail",
            args=[self.publish.year, self.publish.month, self.publish.day, self.slug,],
        )

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

class Comment(models.Model):
    post = models.ForeignKey(
        "Post", on_delete=models.CASCADE, related_name="comments"
    )
    name = models.CharField(max_length=100)
    email = models.EmailField()
    body = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True,)
    updated = models.DateTimeField(auto_now=True)
    active = models.BooleanField(default=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["-created_at"]),
        ]

    def __str__(self):
        return f'Comment by {self.name} on {self.post}'

    def get_absolute_url(self):
        return reverse(
            "blog:comment-detail",
            kwargs={'pk': self.pk},
        )
