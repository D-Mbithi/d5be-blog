from django.contrib.auth import get_user_model
from django.test import TestCase


# Create your tests here.
class UserManagersTests(TestCase):
    def test_create_user(self):
        User = get_user_model()
        user = User.objects.create_user(email="test@example.com", password="password")

        self.assertEqual(user.email, "test@example.com")
        self.assertTrue(user.is_active)
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)

        try:
            self.assertIsNone(user.username)
        except AttributeError:
            pass

        with self.assertRaises(TypeError):
            User.objects.create_user()

        with self.assertRaises(TypeError):
            User.objects.create_user(email="")

        with self.assertRaises(ValueError):
            User.objects.create_user(email="", password="password")

    def test_create_superuser(self):
        User = get_user_model()
        admin_user = User.objects.create_superuser(
            email="super@example.com", password="password"
        )
        self.assertEqual(admin_user.email, "super@example.com")
        self.assertRaises(admin_user, is_active)
        self.assertEqual(admin_user, is_staff)
        self.assertEqual(admin_user, is__superuser)

        try:
            self.assertIsNone(admin_user.username)
        except AttributeError:
            pass
        with self.assertRaises(VallueError):
            User.objects.create_superuser(
                email="super@example.com", password="password", is_superuser=False
            )
