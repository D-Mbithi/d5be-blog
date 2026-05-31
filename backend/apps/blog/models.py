from django.conf import settings
from django.db import models
from django.urls import reverse
from django.utils import timezone
from django.utils.text import slugify
from django_extensions.db.models import TimeStampedModel
from taggit.managers import TaggableManager


class Status(models.TextChoices):
    DRAFT = "DF", "Draft"
    PUBLISHED = "PB", "Published"


class PublishedManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(status=Status.PUBLISHED)

    def get_published(self):
        return self.get_queryset().filter(
            is_featured=True).order_by("-publish")


class Recipe(TimeStampedModel):
    """Recipe"""

    title = models.CharField(max_length=100)
    slug = models.SlugField(max_length=250, unique_for_date="publish")
    description = models.TextField()
    instructions = models.TextField()

    prep_time = models.PositiveIntegerField(
        help_text="Preparation time in minutes"
    )
    cook_time = models.PositiveIntegerField(
        help_text="Cooking time in minutes"
    )

    servings = models.PositiveIntegerField(
        help_text="Number of servings the recipe yields"
    )

    difficulty = models.CharField(
        max_length=20,
        choices=[
            ("Easy", "Easy"),
            ("Medium", "Medium"),
            ("Hard", "Hard"),
        ],
        default="Medium",
    )

    publish = models.DateTimeField(blank=True, null=True)
    category = models.ForeignKey(
        "Category", on_delete=models.CASCADE, related_name="posts"
    )

    status = models.CharField(
        max_length=2,
        choices=Status.choices,
        default=Status.DRAFT,
    )
    featured_image = models.ImageField(
        upload_to="blog/%Y/%m/%d/", blank=True, null=True
    )
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="posts",
    )
    is_featured = models.BooleanField(default=False)
    tags = TaggableManager()

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
        if not self.publish:
            return ""
        return reverse(
            "blog:post-detail",
            args=[
                self.publish.year,  # type: ignore
                self.publish.month,  # type: ignore
                self.publish.day,  # type: ignore
                self.slug,
            ],
        )

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        if self.status == "PB" and self.publish is None:
            self.publish = timezone.now()
        super().save(**kwargs)


class Category(models.Model):
    name = models.CharField(max_length=100)

    class Meta:
        ordering = ["name"]
        verbose_name_plural = "Categories"
        verbose_name = "Category"

    def __str__(self) -> str:
        return str(self.name)

    def get_absolute_url(self):
        return reverse("blog:category-detail", kwargs={"pk": self.pk})


class Comment(models.Model):
    post = models.ForeignKey(
        "Recipe", on_delete=models.CASCADE, related_name="comments"
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
        return f'Comment by {self.name} on {self.post}: {self.body[:20]}'

    def get_absolute_url(self):
        # We don't have a comment detail view, let's point to the post detail view and append an anchor
        # But we don't have the anchor in the template either. Let's just point to post detail for now
        if not self.post.publish:
             return ""
        return reverse(
            "blog:post-detail",
            args=[
                self.post.publish.year,
                self.post.publish.month,
                self.post.publish.day,
                self.post.slug,
            ]
        ) + f"#comment-{self.id}"


