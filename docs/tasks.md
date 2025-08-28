# Improvement Tasks Checklist

Date: 2025-08-10 18:18

Note: Each task is actionable and intended to be checked off when completed. The sequence is ordered from foundational/architectural tasks to code-level fixes, testing, and DX.

1. [ ] Introduce environment-driven settings: read DEBUG, ALLOWED_HOSTS, EMAIL_BACKEND, and feature flags (e.g., ENABLE_SILK) from .env using django-environ.
2. [ ] Set DEBUG = env.bool("DEBUG", default=False); remove hardcoded True in config/settings.py.
3. [ ] Replace ALLOWED_HOSTS = ["*"] with env.list("ALLOWED_HOSTS", default=["127.0.0.1", "localhost"]).
4. [ ] Gate profiling and dev-only apps/middleware (silk, django_extensions, django_seed) behind DEBUG or dedicated env flags.
5. [ ] Add security headers and production hardening toggled by DEBUG: SECURE_SSL_REDIRECT, SESSION_COOKIE_SECURE, CSRF_COOKIE_SECURE, SECURE_HSTS_SECONDS, SECURE_REFERRER_POLICY.
6. [ ] Configure LOGGING dict for request errors, security issues, and app logs (console in DEBUG, file/structured in production).
7. [ ] Add static files production support (e.g., whitenoise.middleware.WhiteNoiseMiddleware) when not using an external static server; collectstatic verified.
8. [ ] Add cache backend configuration via CACHES (locmem for dev, env-driven for prod like Redis) and cache template fragments for list pages.
9. [ ] Add CSRF_TRUSTED_ORIGINS from env for deployments behind a domain/HTTPS.
10. [ ] Create a .env.example file documenting required variables (SECRET_KEY, DEBUG, ALLOWED_HOSTS, EMAIL_BACKEND, ENABLE_SILK, etc.).

11. [ ] Fix models: implement Category.get_absolute_url() to point to a category listing route.
12. [ ] Fix models: update Comment.get_absolute_url() to point to an existing URL (or add the corresponding comment detail route) to avoid reverse errors.
13. [ ] Harden Post.get_absolute_url() or usages: ensure publish is not None when generating URLs (limit calls to published posts or guard with a ValueError if publish is None).
14. [ ] Make created_at fields use auto_now_add=True for Post and Comment to ensure timestamps are set automatically (requires a migration) or set created_at in views before save.
15. [ ] Ensure Post.slug is reliably populated: add pre_save signal or override save() to slugify title when slug is missing (respect unique_for_date constraint).
16. [ ] Add database index/constraints review: confirm existing index on -publish is sufficient; consider adding index on slug and (status, publish) if query patterns require.
17. [ ] Add __str__ clarity for Category and Comment to aid admin/debugging (Category is OK; ensure Comment includes truncated body).
18. [ ] Audit related_name usage for consistency (posts, comments) and document in model docstrings.

19. [ ] Align URLs: standardize naming to kebab-case (e.g., post-list) and fix inconsistent name "postlist" to "post-list-alt" or drop if redundant.
20. [ ] Add a category list/detail route and template, wire to Category.get_absolute_url().
21. [ ] If Comment.get_absolute_url() is kept, add a comment-detail route or remove the method to prevent dead references.
22. [ ] Add route for creating comments via POST on a post detail (dedicated endpoint or same detail view handling POST) with proper CSRF and redirects.

23. [ ] Improve views security and behavior: decorate create/update/delete with @login_required and appropriate permissions/ownership checks.
24. [ ] Replace post_delete DELETE-only handler with POST (use require_POST decorator); add success redirect and messages; include CSRF in template form.
25. [ ] In post_create and post_update, on successful save redirect to the object’s get_absolute_url; add messages.success feedback.
26. [ ] In list/detail views, use select_related('author', 'category') and prefetch_related('comments') to reduce query count.
27. [ ] Simplify pagination in post_list: rely on Paginator.get_page() only; remove redundant try/except for PageNotAnInteger/EmptyPage.
28. [ ] Add error handling/logging around send_mail in post_share; consider throttling or CAPTCHA if exposed publicly.
29. [ ] Implement post_comment: validate CommentForm, set post relation, save, and redirect back to post detail with anchor.
30. [ ] Ensure post_detail only exposes published posts (already filters by publish date) and handles 404 for drafts explicitly.

31. [ ] Expand PostForm fields to include category and optional status; set created_at in the view (timezone.now()) if not switching to auto_now_add.
32. [ ] Generate slug from title in the create view if not provided by model layer; prevent duplicates by appending short suffix when needed.
33. [ ] Add basic validation to CategoryForm (e.g., clean_name to normalize whitespace and enforce case-insensitive uniqueness if desired).
34. [ ] Ensure CommentForm enforces minimal content length and sanitizes/escapes output (template uses autoescape by default; consider bleach if allowing HTML).

35. [ ] Templates: replace hardcoded dates with publish|date and display timezone-aware values.
36. [ ] Templates: replace placeholder images with fields or a default static; add meaningful alt text for images.
37. [ ] Templates: ensure all forms display non_field_errors and field.help_text; style errors visibly.
38. [ ] Templates: add rel and aria attributes for accessibility; ensure color contrast meets AA standards.
39. [ ] Templates: use {% url %} for category links and author profile links if routes exist; avoid href="#" placeholders.
40. [ ] Templates: include SEO basics (title block, meta description block in base, canonical link on detail pages).

41. [ ] Add comprehensive tests:
    - Model tests: slug auto-generation, publish set on status change, get_absolute_url behavior for unpublished posts.
    - View tests: list pagination, detail 404 for drafts, create/update/delete auth and redirects, comment creation.
    - Form tests: PostForm clean/slug logic, CommentForm validation.
42. [ ] Add a tests/ package for blog with __init__.py; keep legacy tests.py if needed; follow guidelines for discovery.
43. [ ] Add factories (factory_boy) or simple helper methods to create users/posts/categories for tests.
44. [ ] Ensure SECRET_KEY and DEBUG are injected for tests via .env in CI; update guidelines if necessary.

45. [ ] Set up CI (GitHub Actions): install deps, create .env with SECRET_KEY, run migrations, run tests, and collectstatic dry run.
46. [ ] Add pre-commit hooks (black, isort, flake8, django-upgrades) and run on CI.
47. [ ] Add mypy (optional) with django-stubs for stricter typing in apps code.
48. [ ] Add coverage report generation and a minimum threshold (e.g., 80%).

49. [ ] Admin: register Category, Post, Comment with list_display/search_fields; use list_filter for status/category; add readonly_fields for publish/created_at.
50. [ ] Admin: add inlines for Comment under Post; add actions to publish/unpublish.

51. [ ] Performance: add DB indices based on query plans (e.g., on (status, -publish), slug); review silk profiling in DEBUG.
52. [ ] Performance: paginate consistently (same page size) and document; consider caching the post list page.

53. [ ] Documentation: update README with setup, .env, running tests, and Tailwind workflow; link to this tasks.md.
54. [ ] Documentation: ensure .junie/guidelines.md stays in sync (noting tests/ structure and CI requirements).
55. [ ] Create CONTRIBUTING.md outlining branch strategy, commit conventions, and code review checklist.

56. [ ] DX: add makefile or justfile for common commands (runserver, migrate, test, lint, format, tailwind-dev).
57. [ ] DX: pin Python and Node versions (pyproject/tool-versions or .tool-versions/asdf) for reproducibility.
58. [ ] DX: add dotenv loading for manage.py (optional) to ease local runs if .env missing.

59. [ ] Security: validate and limit fields accepted in forms/views (e.g., prevent mass assignment); use get_user_model consistently (already used in tests guidance).
60. [ ] Security: add password validators already present; document strong password policy; ensure admin is not exposed in production without protection.
