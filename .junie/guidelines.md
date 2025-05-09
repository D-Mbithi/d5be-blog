# Development Guidelines for d5be-blog

This document provides guidelines and instructions for developing and maintaining the d5be-blog project.

## Build/Configuration Instructions

### Python Environment Setup

The project uses both Pipenv and requirements.txt for dependency management. Pipenv is recommended for development.

#### Using Pipenv (Recommended)

1. Install Pipenv if you don't have it:
   ```bash
   pip install pipenv
   ```

2. Install dependencies:
   ```bash
   pipenv install
   ```

3. Activate the virtual environment:
   ```bash
   pipenv shell
   ```

#### Using pip and requirements.txt (Alternative)

```bash
pip install -r requirements.txt
```

### Environment Variables

The project uses django-environ to manage environment variables. Create a `.env` file in the project root with the following variables:

```
SECRET_KEY=your_secret_key_here
DEBUG=True
```

### Database Setup

The project uses SQLite by default. To set up the database:

```bash
python manage.py migrate
```

### Frontend Setup

The project uses Tailwind CSS for styling:

1. Install Node.js dependencies:
   ```bash
   npm install
   ```

2. Run Tailwind CSS compilation:
   ```bash
   npm run dev
   ```

### Running the Development Server

```bash
python manage.py runserver
```

## Testing Information

### Running Tests

To run all tests:

```bash
python manage.py test
```

To run tests for a specific app:

```bash
python manage.py test apps.blog.tests
```

### Creating New Tests

Tests should be placed in a `tests.py` file within each app directory or in a `tests` directory if there are multiple test files.

#### Example Test

Here's an example test for the Post model in the blog app:

```python
from django.test import TestCase
from django.utils import timezone
from django.contrib.auth import get_user_model

from .models import Post, Category, Status


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
        post = Post.objects.create(
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
```

### Test Database

When running tests, Django creates a test database, which is separate from your development database. This ensures that your tests don't affect your development data.

## Additional Development Information

### Project Structure

- `apps/`: Contains Django applications
  - `blog/`: Blog application
  - `users/`: User authentication and profiles
- `config/`: Project configuration
- `static/`: Static files
- `templates/`: HTML templates

### Custom User Model

The project uses a custom user model defined in `apps.users.models.CustomUser`. Always use `get_user_model()` to reference the user model in your code.

### Database Migrations

After making changes to models, create and apply migrations:

```bash
python manage.py makemigrations
python manage.py migrate
```

### Frontend Development

The project uses Tailwind CSS for styling. The CSS is compiled from `static/src/input.css` to `static/css/styles.css`.

To watch for changes and recompile automatically:

```bash
npm run dev
```

### Admin Interface

The project uses django-admin-soft-dashboard for a custom admin interface.

### Performance Monitoring

The project includes django-silk for performance profiling. Access it at `/silk/` when the development server is running.

### Code Style

The project follows standard Django conventions:
- Class names use CamelCase
- Function and variable names use snake_case
- Models have a descriptive docstring
- Custom managers are used for common queries (e.g., PublishedManager)
