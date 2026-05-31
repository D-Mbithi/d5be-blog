from django.test import TestCase
from django.utils import timezone
from django.contrib.auth import get_user_model

from .models import Recipe, Category, Status


class PostModelTests(TestCase):
    def setUp(self):
        # Create a test user
        User = get_user_model()
        self.user = User.objects.create_user(
            email="test@example.com",
            password="testpassword"
        )

        # Create a test category
        self.category = Category.objects.create(name="Test Category")

    def test_post_publish_date_set_on_publish(self):
        """Test that publish date is set when status changes to published"""
        # Create a draft post
        post = Recipe.objects.create(
            title="Test Post",
            slug="test-post",
            body="This is a test post body",
            created_at=timezone.now(),
            category=self.category,
            author=self.user,
            status=Status.DRAFT
        )

        # Verify publish date is None
        self.assertIsNone(post.publish)

        # Change status to published and save
        post.status = Status.PUBLISHED
        post.save()

        # Verify publish date is set
        self.assertIsNotNone(post.publish)
