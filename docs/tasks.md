# Recipe Sharing Blog Improvement Tasks Checklist

Date: 2026-05-22

Note: Each task is actionable and intended to be checked off when completed. The sequence is ordered from foundational/architectural tasks to code-level fixes, testing, and DX. The checklist is aligned with the current recipe-sharing blog direction in `templates/index.html` and the profile/user flow in `apps/users`.

1. [ ] Introduce environment-driven settings: read `DEBUG`, `ALLOWED_HOSTS`, `EMAIL_BACKEND`, and feature flags (e.g. `ENABLE_SILK`) from `.env` using `django-environ`.
2. [ ] Set `DEBUG = env.bool("DEBUG", default=False)`; remove hardcoded `True` in `config/settings.py`.
3. [ ] Replace `ALLOWED_HOSTS = ["*"]` with `env.list("ALLOWED_HOSTS", default=["127.0.0.1", "localhost"])`.
4. [ ] Gate profiling and dev-only apps/middleware (`silk`, `django_extensions`, `django_seed`) behind `DEBUG` or dedicated env flags.
5. [ ] Add security headers and production hardening toggled by `DEBUG`: `SECURE_SSL_REDIRECT`, `SESSION_COOKIE_SECURE`, `CSRF_COOKIE_SECURE`, `SECURE_HSTS_SECONDS`, `SECURE_REFERRER_POLICY`.
6. [ ] Configure `LOGGING` dict for request errors, security issues, and app logs (console in DEBUG, file/structured in production).
7. [ ] Add static files production support (e.g. `whitenoise.middleware.WhiteNoiseMiddleware`) when not using an external static server; verify `collectstatic`.
8. [ ] Add cache backend configuration via `CACHES` (locmem for dev, env-driven for prod like Redis) and cache template fragments for recipe list pages.
9. [ ] Add `CSRF_TRUSTED_ORIGINS` from env for deployments behind a domain/HTTPS.
10. [ ] Create a `.env.example` file documenting required variables (`SECRET_KEY`, `DEBUG`, `ALLOWED_HOSTS`, `EMAIL_BACKEND`, `ENABLE_SILK`, etc.).

11. [ ] Fix models: implement `Category.get_absolute_url()` to point to a recipe category listing route.
12. [ ] Fix models: update `Comment.get_absolute_url()` to point to an existing URL (or add the corresponding comment detail route) to avoid reverse errors.
13. [ ] Harden `Post.get_absolute_url()` or usages: ensure `publish` is not `None` when generating URLs (limit calls to published recipes or guard with a `ValueError` if `publish` is `None`).
14. [ ] Make `created_at` fields use `auto_now_add=True` for `Post` and `Comment` to ensure timestamps are set automatically (requires a migration) or set `created_at` in views before save.
15. [ ] Ensure `Post.slug` is reliably populated: add `pre_save` signal or override `save()` to slugify title when slug is missing (respect `unique_for_date` constraint).
16. [ ] Add database index/constraints review: confirm existing index on `-publish` is sufficient; consider adding index on `slug` and `(status, publish)` if query patterns require.
17. [ ] Add `__str__` clarity for `Category` and `Comment` to aid admin/debugging (`Category` is OK; ensure `Comment` includes truncated body).
18. [ ] Audit `related_name` usage for consistency (`posts`, `comments`) and document in model docstrings.

19. [ ] Align URLs: standardize naming to kebab-case (e.g. `post-list`) and fix inconsistent name `postlist` to `post-list-alt` or drop if redundant.
20. [ ] Add a category list/detail route and template, wire to `Category.get_absolute_url()`.
21. [ ] If `Comment.get_absolute_url()` is kept, add a comment-detail route or remove the method to prevent dead references.
22. [ ] Add route for creating comments via POST on a recipe detail (dedicated endpoint or same detail view handling POST) with proper CSRF and redirects.
23. [ ] Add routes for profile viewing and profile editing so users can manage their culinary bio and avatar.

24. [ ] Improve views security and behavior: decorate create/update/delete with `@login_required` and appropriate permissions/ownership checks.
25. [ ] Replace `post_delete` DELETE-only handler with POST (use `require_POST` decorator); add success redirect and messages; include CSRF in template form.
26. [ ] In `post_create` and `post_update`, on successful save redirect to the object’s `get_absolute_url`; add `messages.success` feedback.
27. [ ] In list/detail views, use `select_related("author", "category")` and `prefetch_related("comments")` to reduce query count.
28. [ ] Simplify pagination in `post_list`: rely on `Paginator.get_page()` only; remove redundant try/except for `PageNotAnInteger`/`EmptyPage`.
29. [ ] Add error handling/logging around `send_mail` in `post_share`; consider throttling or CAPTCHA if exposed publicly.
30. [ ] Implement `post_comment`: validate `CommentForm`, set post relation, save, and redirect back to recipe detail with anchor.
31. [ ] Ensure `post_detail` only exposes published recipes (already filters by publish date) and handles 404 for drafts explicitly.
32. [ ] Add profile views for displaying a user’s profile and editing their bio/avatar, matching the recipe-sharing site design.

33. [ ] Expand `PostForm` fields to include category and optional status; set `created_at` in the view (`timezone.now()`) if not switching to `auto_now_add`.
34. [ ] Generate slug from title in the create view if not provided by model layer; prevent duplicates by appending short suffix when needed.
35. [ ] Add basic validation to `CategoryForm` (e.g. `clean_name` to normalize whitespace and enforce case-insensitive uniqueness if desired).
36. [ ] Ensure `CommentForm` enforces minimal content length and sanitizes/escapes output (template uses autoescape by default; consider bleach if allowing HTML).
37. [ ] Add a profile form for editing first name, last name, email, username, bio, and profile image if the UX requires it.

38. [ ] Templates: replace hardcoded dates with `publish|date` and display timezone-aware values.
39. [ ] Templates: replace placeholder images with fields or a default static; add meaningful alt text for recipe images and profile avatars.
40. [ ] Templates: ensure all forms display `non_field_errors` and `field.help_text`; style errors visibly.
41. [ ] Templates: add `rel` and `aria` attributes for accessibility; ensure color contrast meets AA standards.
42. [ ] Templates: use `{% url %}` for category links, recipe links, and author profile links if routes exist; avoid `href="#"` placeholders.
43. [ ] Templates: include SEO basics (title block, meta description block in base, canonical link on detail pages).
44. [ ] Templates: keep the homepage consistent with the existing recipe-focused design language (hero recipe, filter chips, cards, chef spotlight, newsletter block).
45. [ ] Templates: add a dedicated profile page layout that matches the same visual system as `templates/index.html`.

46. [ ] Add comprehensive tests:
    - Model tests: slug auto-generation, publish set on status change, `get_absolute_url` behavior for unpublished recipes.
    - View tests: list pagination, detail 404 for drafts, create/update/delete auth and redirects, comment creation, profile page rendering.
    - Form tests: `PostForm` clean/slug logic, `CommentForm` validation, profile form validation.
47. [ ] Add a `tests/` package for blog with `__init__.py`; keep legacy `tests.py` if needed; follow guidelines for discovery.
48. [ ] Add factories (`factory_boy`) or simple helper methods to create users/posts/categories/profiles for tests.
49. [ ] Ensure `SECRET_KEY` and `DEBUG` are injected for tests via `.env` in CI; update guidelines if necessary.

50. [ ] Set up CI (GitHub Actions): install deps, create `.env` with `SECRET_KEY`, run migrations, run tests, and `collectstatic` dry run.
51. [ ] Add pre-commit hooks (`black`, `isort`, `flake8`, `django-upgrades`) and run on CI.
52. [ ] Add mypy (optional) with `django-stubs` for stricter typing in apps code.
53. [ ] Add coverage report generation and a minimum threshold (e.g. 80%).

54. [ ] Admin: register `Category`, `Post`, `Comment` with `list_display`/`search_fields`; use `list_filter` for status/category; add `readonly_fields` for publish/created_at.
55. [ ] Admin: add inlines for `Comment` under `Post`; add actions to publish/unpublish.
56. [ ] Admin: consider profile visibility or moderation tools if chef-style author pages become editorially managed.

57. [ ] Performance: add DB indices based on query plans (e.g. on `(status, -publish)`, `slug`); review Silk profiling in DEBUG.
58. [ ] Performance: paginate consistently (same page size) and document; consider caching the recipe list page and category blocks.
59. [ ] Performance: optimize homepage media delivery for recipe cards and profile images.

60. [ ] Documentation: update README with setup, `.env`, running tests, and Tailwind workflow; link to this tasks.md.
61. [ ] Documentation: ensure `.junie/guidelines.md` stays in sync (noting tests/ structure and CI requirements).
62. [ ] Create `CONTRIBUTING.md` outlining branch strategy, commit conventions, and code review checklist.

63. [ ] DX: add `Makefile` or `justfile` for common commands (`runserver`, `migrate`, `test`, `lint`, `format`, `tailwind-dev`).
64. [ ] DX: pin Python and Node versions (`pyproject`/`.tool-versions`/asdf) for reproducibility.
65. [ ] DX: add dotenv loading for `manage.py` (optional) to ease local runs if `.env` is missing.

66. [ ] Security: validate and limit fields accepted in forms/views (e.g. prevent mass assignment); use `get_user_model` consistently.
67. [ ] Security: add password validators already present; document strong password policy; ensure admin is not exposed in production without protection.

68. [ ] Recipe-sharing enhancements: add saved/favorite recipes for users.
69. [ ] Recipe-sharing enhancements: add recipe ratings or likes if community engagement is in scope.
70. [ ] Recipe-sharing enhancements: add structured recipe metadata like prep time, cook time, servings, difficulty, ingredients, and steps.
71. [ ] Recipe-sharing enhancements: add featured recipe selection for the homepage and category landing pages.
72. [ ] Recipe-sharing enhancements: add author/chef spotlight content and profile badges where appropriate.
73. [ ] Recipe-sharing enhancements: add newsletter signup handling and confirmation flow if email capture becomes real backend functionality.