# AGENTS.md - AI Agent Guide for Django Recipe Blog

## Project Overview

A Django 6.0+ recipe/blog platform with PostgreSQL backend, Tailwind CSS frontend, and custom user authentication. The project features a recipe management system (confusingly called "Recipe" model but represents blog posts), user profiles, comments, and tagging. Built with `uv` for dependency management.

## Architecture Overview

### Core Apps Structure
- **`apps/blog/`** - Recipe/post management (listings, creation, publishing)
- **`apps/users/`** - User accounts and profiles (custom auth, profile editing)
- **`config/`** - Django project settings and URL routing

### Critical Data Flow
1. **User Creation** → Auto-triggers `Profile` creation via `post_save` signal (apps/users/models.py:41-46)
2. **Recipe Publishing** → Auto-sets `publish` timestamp and slug via `save()` override (apps/blog/models.py:99-104)
3. **Recipe Slugs** → Generated from title; combined with publish date for unique URLs
4. **Comments** → Attached to recipes but don't require login; moderated via `active` flag

### User Authentication
- Custom `CustomUser` model (apps/users/models.py) with **email as USERNAME_FIELD** (not username)
- Auth backends: Django native + django-allauth (config/settings.py:162-165)
- Profile auto-created as OneToOne relation when CustomUser is created
- Email verification disabled via `ACCOUNT_EMAIL_VERIFICATION = 'none'`

### Key Integration Points
- **Tagging**: django-taggit TaggableManager on Recipe model
- **Image Handling**: Pillow for profile pics and featured images; stored in `media/` with auto-upload paths
- **Email**: django-anymail with Resend backend (requires RESEND_API_KEY env var)
- **Task Queue**: django-tasks-db with database backend (no Celery)

## Essential Workflows

### Starting Development
```bash
# Dependencies via uv (modern Python package manager)
uv sync                    # Install from pyproject.toml
uv venv                    # Create virtual environment

# Database setup
python manage.py migrate

# Generate test recipe data (custom command)
python manage.py generate_test_data --users 6 --posts 24 --comments 72

# CSS compilation (requires npm)
npm install               # Install Tailwind & Flowbite
npm run dev              # Watch static/src/input.css → static/css/styles.css
```

### Running the Server
```bash
python manage.py runserver
# Access at http://localhost:8000
# Admin panel: /admin/ (use generated test user or create superuser)
# Debug toolbar (Silk): /silk/ (DEBUG=True only)
```

### Project-Specific npm/Python Scripts
- `npm run dev` - Tailwind CSS watch mode (required for style changes)
- `python manage.py generate_test_data` - Populates recipes with realistic data and test users (use for demos)
- No formal test suite; uses Django's test framework but not configured

### Configuration Files & Env Variables
- **`.env` file** (loaded by django-environ): `DEBUG`, `SECRET_KEY`, `DATABASE_*`, `RESEND_API_KEY`, `ALLOWED_HOSTS`
- **`config/settings.py`** - All Django config; defaults to PostgreSQL (won't work without DB_HOST, etc.)
- **`pyproject.toml`** - Dependencies (Django 6.0+, django-allauth, anymail, taggit, silk, etc.)
- **`tailwind.config.js`** - Scans templates/ and node_modules/flowbite for Tailwind classes

## Common Code Patterns

### Recipe/Post CRUD with Owner Authorization
```python
# apps/blog/views.py: post_update() & post_delete() pattern
@login_required
def post_update(request, post_id):
    post = get_object_or_404(Recipe, id=post_id)
    if post.author != request.user:        # Ownership check
        raise Http404("Not authorized")
    # Form handling...
```
**Note**: Uses Http404 for permission denial (not PermissionDenied), visible to non-logged-in users.

### Published vs. Draft Filtering
```python
# apps/blog/models.py - Custom manager pattern
Recipe.published.all()     # Only status='PB' and publish is set
Recipe.objects.all()       # All recipes including drafts
```
Always use `.published` in public views; `.objects.all()` only in admin/detail views.

### Form-Based CRUD with File Uploads
```python
# apps/blog/views.py: post_create() pattern
if form.is_valid():
    post = form.save(commit=False)
    post.author = request.user             # Set owner before save
    post.save()
    form.save_m2m()                        # Save m2m fields (tags)
```
**Important**: Tags are M2M; must call `form.save_m2m()` when using `commit=False`.

### Email Sending (Async Pattern via django-tasks-db)
```python
# apps/blog/views.py: post_share()
send_mail(subject=..., message=..., from_email=None, recipient_list=[...])
```
Uses django-anymail with Resend. Email is sent synchronously in view (not queued); to make async, wrap with `django_tasks`.

### Auto-Slug Generation in save()
```python
# apps/blog/models.py: Recipe.save()
if not self.slug:
    self.slug = slugify(self.title)       # Auto-generate slug if missing
if self.status == "PB" and self.publish is None:
    self.publish = timezone.now()         # Auto-set publish time when status changes to Published
```

### Signal-Based Profile Creation
```python
# apps/users/models.py
@receiver(post_save, sender=CustomUser, dispatch_uid="create_profile_object")
def create_profile_object(sender, instance, created, **kwargs):
    if created and not kwargs.get("raw"):  # Skip during fixtures
        Profile.objects.get_or_create(user=instance)
```

## URL Routing Map

```
/                          → views.post_list (paginated recipes)
/admin/                    → Django admin (staff only)
/silk/                     → Django Silk profiler (DEBUG=True)
/recipes/                  → RecipeListView (CBV)
/recipes/<year>/<month>/<day>/<slug>/   → post_detail() function-based view
/recipes/<pk>/             → CategoryDetailView (CBV)
/accounts/                 → allauth routes (signup, login, password reset)
/accounts/profile/<id>/    → profile_view()
/accounts/profile/<id>/edit/ → edit_profile()
```

## Development Gotchas & Project-Specific Behaviors

### 1. Model Naming Confusion
- Model named `Recipe` represents blog **posts/articles** (not actual recipes initially, but now recipes!)
- "Post" terminology in code (views, URLs) but model is `Recipe`
- Fixture file: `fixtures/recipe_fixtures.json`

### 2. Custom User Email Authentication
- Users authenticate with **email**, not username (`USERNAME_FIELD = 'email'`)
- Unique email constraint; username is separate field (optional)
- Profile accessed via `user.profile` (OneToOne reverse relation)

### 3. Publish Workflow
- Recipes must have `status='PB'` (Published) AND non-null `publish` datetime to appear publicly
- Routes include year/month/day slugs based on `publish` date
- Draft recipes inaccessible to public (Http404), but visible in admin

### 4. Comment Moderation
- Comments have `active` boolean flag
- Only active comments appear in template
- Requires admin approval (not auto-activated); set `active=True` manually in admin

### 5. Admin Customization
- `PostAdmin` has `date_hierarchy = "publish"` for drill-down filtering
- `show_facets = admin.ShowFacets.ALWAYS` (Django 5.0+) for sidebar facets
- Raw ID fields for author (lookup instead of dropdown)
- Slug auto-populates from title in form

### 6. Development-Only Features
- Django Silk (`/silk/`) for request profiling (added to INSTALLED_APPS only if DEBUG=True)
- Browser reload middleware auto-injects viewport reload script (DEBUG mode)
- No fake data during migrations (signals check `kwargs.get("raw")` to skip during fixtures)

### 7. Environment-Dependent Behavior
- **Debug=True**: Tailwind/static served by Django, Silk enabled, browser reload active
- **Debug=False**: HTTPS redirect, secure cookies, HSTS headers enabled (config/settings.py:182-187)

## Database Schema Essentials

### Primary Models
- **CustomUser** - extends Django AbstractUser; email is unique identifier
- **Profile** - OneToOne with CustomUser; user profile metadata
- **Recipe** - Main blog post model; has author (FK), category (FK), tags (M2M via taggit)
- **Category** - Recipe categorization; simple name + ordering
- **Comment** - Attached to recipes; has active flag and auto-timestamps

### Indexes
- Recipe: index on `-publish` for homepage queries
- Comment: index on `-created_at` for ordering

### Ordering Defaults
- Recipe: ordered by `-publish` (newest first)
- Category: ordered by `name` alphabetically
- Comment: ordered by `-created_at` (newest first)

## File Organization Rules

- **Templates**: `templates/` (base.html, index.html) + per-app folders (blog/, account/)
- **Partials**: `templates/partials/` (header, pagination, posts)
- **Static Assets**: `static/css/`, `static/imgs/`, `static/src/input.css`
- **Media**: `media/profile_pics/` (user uploads), `media/blog/YYYY/MM/DD/` (featured images)
- **Management Commands**: `apps/blog/management/commands/` (Django convention)
- **Fixtures**: `fixtures/recipe_fixtures.json`

## Key Dependencies & Why They're Used

| Package | Purpose | Config Location |
|---------|---------|-----------------|
| django-allauth | Social auth + account management | config/settings.py:38-40 |
| django-taggit | Flexible tagging system | Recipe.tags field |
| django-anymail | Email abstraction (uses Resend) | config/settings.py:170-173 |
| django-extensions | TimeStampedModel, shell_plus | apps/users/models.py:4 |
| django-silk | Performance profiling | Added to INSTALLED_APPS if DEBUG |
| django-tasks-db | Background task queue (minimal) | config/settings.py:176-179 |
| tailwindcss | CSS utility framework | tailwind.config.js + npm |
| flowbite | UI component library | tailwind.config.js, cdn in templates |

## Common Debugging Approaches

### View a Recipe's Full URL
Use `recipe.get_absolute_url()` - returns `/recipes/year/month/day/slug/` or empty string if not published

### Check Published vs Drafts
```python
Recipe.published.all()  # Only public recipes (status='PB' + publish set)
Recipe.objects.all()    # All recipes
```

### Inspect User-Recipe Relations
```python
user.posts.all()        # All recipes by this user (author FK relation)
user.profile            # User's profile (OneToOne)
```

### Test Email Sending Locally
Set `EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"` to print emails to console instead of Resend

### Profiling View Performance
Visit `/silk/` (if DEBUG=True) to see request/response times, template renders, query counts

---

**Last Updated**: May 2026 | **Django Version**: 6.0+ | **Python**: 3.12+

