d5be-blog: Development Guidelines (Project-Specific)

This document records project-specific practices that help advanced contributors get productive quickly and avoid common pitfalls. It assumes familiarity with Django and typical tooling. Use it as a living note for decisions and verified workflows.

1. Build / Configuration
- Python environment
  - The repo ships with both Pipenv and requirements.txt. Pipenv is preferred in development.
  - Recommended:
    - pip install pipenv
    - pipenv install
    - pipenv shell
  - Alternative:
    - pip install -r requirements.txt
- Environment variables
  - Settings are configured via django-environ. A .env file at project root is required because SECRET_KEY is accessed as env('SECRET_KEY') with no default and will raise if missing.
  - Minimal .env for local/dev and tests:
    - SECRET_KEY=any-non-empty-string
    - DEBUG=True
- Database
  - SQLite is the default (config/settings.py -> db.sqlite3). No extra services required.
  - Migrations are present for apps.users and apps.blog; tests run against a transient in-memory test DB and apply migrations automatically.
- Static & media
  - STATICFILES_DIRS points at ./static and STATIC_ROOT at ./staticroot.
  - MEDIA_ROOT is ./media.
- Frontend (Tailwind)
  - npm install
  - npm run dev (watches and compiles static/css/styles.css from static/src/input.css via tailwind.config.js)
- Admin & profiling additions
  - django-admin-soft-dashboard is enabled for a custom admin theme.
  - django-silk is installed and middleware is enabled; when the dev server runs, profiling is available at /silk/.

2. Testing: How to run, add, and execute
- Important gotchas for this repo
  - SECRET_KEY must be available or tests will error during settings load. Provide it via .env as shown above.
  - The blog app contains both a legacy tests.py and may also contain a tests/ directory if you add one. If you create a tests/ directory, add an empty __init__.py so Django/pytest/unittest discovery treats it as a package.
  - Custom user model (apps.users.models.CustomUser) uses email as USERNAME_FIELD and has no username. Always use get_user_model() in tests.
- Running tests
  - Run all tests:
    - python manage.py test
  - Run tests for the blog app legacy module:
    - python manage.py test apps.blog.tests
  - Run a specific test module inside a tests/ package (recommended precision):
    - python manage.py test apps.blog.tests.test_smoke
  - Use -v 2 for verbose output.
- Adding a new test (verified example)
  - Pattern 1: single-module tests (legacy): apps/blog/tests.py
    - Tests in this file are auto-discovered when you run python manage.py test apps.blog.tests.
  - Pattern 2: package tests: apps/blog/tests/
    - Create the directory and add __init__.py in it. Place files like test_something.py.
  - Minimal model behavior test (works as of 2025-08-10)
    - Verified by running: python manage.py test apps.blog.tests.test_smoke -v 2
    - Example content used during verification (this is safe to replicate in a new file):
      
      from django.test import TestCase
      from django.utils import timezone
      from django.contrib.auth import get_user_model
      
      from apps.blog.models import Post, Category, Status
      
      class BlogSmokeTests(TestCase):
          def setUp(self):
              User = get_user_model()
              self.user = User.objects.create_user(
                  email="smoke@example.com", password="smokepass"
              )
              self.category = Category.objects.create(name="SmokeCat")
          
          def test_post_publish_date_set_on_publish(self):
              post = Post.objects.create(
                  title="Smoke Post",
                  slug="smoke-post",
                  body="Body",
                  created_at=timezone.now(),
                  category=self.category,
                  author=self.user,
                  status=Status.DRAFT,
              )
              self.assertIsNone(post.publish)
              post.status = Status.PUBLISHED
              post.save()
              self.assertIsNotNone(post.publish)
  - Notes about Post model constraints
    - slug has unique_for_date='publish'. Creating DRAFT posts with None publish is fine; uniqueness is evaluated when publish is set. The save() override will set publish to timezone.now() when status == PUBLISHED and publish is None, which is what the test exercises.

3. Additional Development Information
- Project structure
  - apps/
    - users/: Custom user model with email as primary login; Profile related via OneToOne. Use get_user_model() consistently to avoid coupling.
    - blog/: Post/Category/Comment with PublishedManager and Status enum. Post.save() auto-sets publish on first transition to published.
  - config/: Django settings/urls; settings import .env via django-environ; TIME_ZONE is Africa/Nairobi.
  - templates/, static/, staticroot/, media/: standard layout; Tailwind is configured via tailwind.config.js.
- Email settings
  - EMAIL_BACKEND is configured to console backend in settings for development. Sending emails in dev prints to stdout.
- Admin/profiling
  - Admin Soft dashboard is installed and configured via admin_soft.apps.AdminSoftDashboardConfig.
  - Silk profiling middleware is enabled; visit /silk/ after running the dev server to inspect requests and queries.
- Common pitfalls
  - Missing .env leads to ImproperlyConfigured: Set the SECRET_KEY environment variable.
  - If you create a tests/ directory in any app, ensure there is an __init__.py to avoid discovery edge cases when mixing tests.py and tests/ package.
  - Always create Post with created_at set; the field is required. publish may be left None for drafts and will be set on publish transition.
- Useful commands
  - Database setup (dev): python manage.py migrate
  - Run server: python manage.py runserver
  - Seed data (django-seed installed): see django-seed docs; not pre-wired with custom commands here.

Quickstart (tested 2025-08-14)
- Python deps (preferred): pip install pipenv && pipenv install && pipenv shell
- Alt: pip install -r requirements.txt
- Frontend: npm install && npm run dev (optional during backend-only work)
- Run dev server: python manage.py runserver
- Run all tests with inline env (no .env file needed): SECRET_KEY=dev DEBUG=True python manage.py test -v 2

Appendix: Verified Test Run Transcript (2025-08-14)
- Command executed: SECRET_KEY=devsecret DEBUG=True python manage.py test apps.blog.tests -v 2
- Result: Ran 1 test; OK; migrations applied to in-memory test DB; no system check issues.

Maintenance Notes
- Keep this document updated when test discovery conventions change (e.g., migrating fully to tests/ packages).
- If adding CI, ensure the workflow creates a .env (at least SECRET_KEY) or injects SECRET_KEY via environment before running tests.
