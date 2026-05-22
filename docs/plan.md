# Recipe Sharing Blog Improvement Plan

Date: 2026-05-22
Source basis: This plan is synthesized from the available repository context, especially `docs/tasks.md`, `docs/guidelines.md`, the Django app structure, and the current recipe-focused UI in `templates/index.html`. The project is treated as a recipe-sharing blog for Gourmet Recipes & Culinary Inspiration.

## 1) Key Goals and Constraints

- Configuration and deployment
  - Settings should remain environment-driven via `django-environ`; a `.env` file is required with at least `SECRET_KEY` and `DEBUG`.
  - Default DB is SQLite; migrations exist; tests run on an ephemeral DB.
  - Tailwind is used for styling; local npm workflow is present.
  - Admin soft dashboard and `django-silk` are enabled during development.

- Security posture
  - Avoid hard-coded `DEBUG=True` and `ALLOWED_HOSTS=["*"]`; support security headers in production.
  - Email backend defaults to console in development; production-safe configuration is required.

- Domain model and behavior
  - The site is a **recipe-sharing blog** rather than a generic blog.
  - Core content centers on recipe posts, categories, comments, and author profiles.
  - `Post.save()` sets publish timestamp on first publish.
  - Slug uniqueness relates to publish date (`unique_for_date`); `created_at` is currently required.

- UX and templates
  - Accessible, SEO-friendly templates; correct timezone display; remove placeholders.
  - Homepage should reflect the recipe-oriented design language already used in `templates/index.html`:
    featured recipe hero, category filters, recipe cards, chef spotlight, newsletter CTA, and a polished footer.

- Testing and CI
  - Tests should cover models, views, forms, and profile behavior.
  - CI should ensure `.env` is present and run `collectstatic` in dry-run or equivalent safe mode.

- Performance and admin
  - Reasonable indexes, consistent pagination, optional caching, and strong admin ergonomics.
  - Recipe browsing should remain fast even as recipe cards, filters, and profile content grow.

## 2) Architecture and Configuration Improvements

### 1) Environment-driven settings
- Actions:
  - Read `DEBUG` via `env.bool("DEBUG", default=False)` and remove hard-coded `True`.
  - Replace `ALLOWED_HOSTS=["*"]` with `env.list("ALLOWED_HOSTS", default=["127.0.0.1", "localhost"])`.
  - Read `EMAIL_BACKEND`, `CSRF_TRUSTED_ORIGINS`, and feature flags such as `ENABLE_SILK` from env.
- Rationale: Secure, reproducible deployments across environments; eliminate risky defaults.

### 2) Dev-only apps/middleware gating
- Actions:
  - Enable Silk, `django_extensions`, and `django_seed` only when `DEBUG` or explicit env flags are true.
- Rationale: Prevents leaking debugging and profiling tools in production.

### 3) Security headers and hardening
- Actions:
  - Configure `SECURE_SSL_REDIRECT`, `SESSION_COOKIE_SECURE`, `CSRF_COOKIE_SECURE`, `SECURE_HSTS_SECONDS`, and `SECURE_REFERRER_POLICY` conditionally on `DEBUG`.
- Rationale: Aligns with Django security guidance for HTTPS deployments.

### 4) Static files in production
- Actions:
  - Add WhiteNoise middleware when not using an external static server; verify `collectstatic`.
- Rationale: Simpler deployments and standard static-file caching.

### 5) Logging
- Actions:
  - Configure `LOGGING` for request errors, security issues, and app logs. Console in debug; structured or file logging in production.
- Rationale: Better operational visibility and incident response.

### 6) Caching
- Actions:
  - Default to `locmem` cache in development; allow Redis via env in production.
  - Cache template fragments for public recipe list pages and category blocks when appropriate.
- Rationale: Improves performance under load.

### 7) `.env.example`
- Actions:
  - Provide a sample with `SECRET_KEY`, `DEBUG`, `ALLOWED_HOSTS`, `EMAIL_BACKEND`, `CSRF_TRUSTED_ORIGINS`, `ENABLE_SILK`, `CACHE_URL`, etc.
- Rationale: Developer onboarding and CI automation.

## 3) Data Model and Integrity

### 1) URL methods
- Actions:
  - Implement `Category.get_absolute_url()` to point to the category listing route.
  - Update `Comment.get_absolute_url()` to point to an existing URL or remove it to avoid reverse errors.
  - Guard `Post.get_absolute_url()` to raise `ValueError` if `publish` is `None`, or restrict usage to published posts.
- Rationale: Prevent broken links and keep recipe navigation consistent.

### 2) Timestamps and slugging
- Actions:
  - Switch `created_at` to `auto_now_add=True` on `Post` and `Comment`, or ensure views set `created_at` explicitly before save.
  - Ensure slug is populated when missing using `pre_save` or a `save()` override with `slugify`.
  - Respect `unique_for_date` and append a short suffix if needed for collisions.
- Rationale: Reliable data defaults and user-friendly recipe URLs.

### 3) Indices and constraints
- Actions:
  - Confirm the existing index on `-publish`.
  - Consider composite index on `(status, publish)` and an index on `slug`.
- Rationale: Faster recipe list/detail queries and filters.

### 4) Developer ergonomics
- Actions:
  - Ensure `__str__` methods are informative.
  - For recipe context, `Comment.__str__` should ideally include a short preview.
  - Audit `related_name` usage for consistency (`posts`, `comments`) and document it in model docstrings.
- Rationale: Better admin usability and maintainability.

## 4) URLs and Navigation

- Standardize URL names to kebab-case where possible.
- Add category list/detail routes and templates; wire to `Category.get_absolute_url()`.
- If keeping `Comment.get_absolute_url()`, introduce a comment-detail route; otherwise remove the method.
- Provide an endpoint to create comments, either via a dedicated POST endpoint or by handling POST in `post_detail`, with proper CSRF and redirects.
- Add recipe-oriented routes if they are part of the product direction:
  - featured recipes
  - latest recipes
  - saved recipes
  - author profile pages
  - profile edit page
- Rationale: Predictable, RESTful routing and better recipe discovery.

## 5) Views and Controllers

- Protect create/update/delete views with `@login_required` and ownership or permission checks.
- Convert delete handling to `require_POST`; add success redirect and messages; include CSRF in the template.
- In create/update, redirect to the object’s `get_absolute_url()` on success and use `messages.success`.
- Optimize list/detail queries with `select_related("author", "category")` and `prefetch_related("comments")`.
- Simplify pagination using `Paginator.get_page()`.
- Wrap `send_mail` in `post_share` with error handling and optional throttling or CAPTCHA if public.
- Implement `post_comment`: validate `CommentForm`, set the post relation, save, and redirect back to the post detail with an anchor.
- Ensure drafts are not exposed by detail view; return 404 for unauthorized or draft access.
- Add profile-related views if needed for:
  - profile display
  - profile editing
  - avatar upload
  - bio updates
- Rationale: Security, usability, and performance improvements.

## 6) Forms and Validation

- `PostForm`: include category and optional status; if `created_at` is not auto-managed, set it in the view.
- Slug handling in create view if not handled in model layer; avoid duplicates with a suffix strategy.
- `CategoryForm`: normalize whitespace and optionally enforce case-insensitive uniqueness.
- `CommentForm`: enforce minimum length; consider sanitization if rich text is allowed.
- Profile forms should support:
  - display name
  - email
  - bio
  - avatar/profile picture
- Rationale: Data quality and safe inputs.

## 7) Templates, Accessibility, and SEO

- Replace hardcoded dates with `publish|date` and ensure timezone-aware display.
- Replace placeholder images with model fields or sensible defaults; always set meaningful alt text.
- Display `non_field_errors` and `field.help_text`; style errors visibly.
- Add `rel` and `aria` attributes where appropriate; ensure color contrast and keyboard focus styles.
- Use `{% url %}` for category, author, profile, and recipe links; remove `href="#"` placeholders.
- Add SEO basics:
  - title blocks
  - meta description blocks in `base.html`
  - canonical link on detail pages
- Keep the homepage design consistent with the existing recipe visual language:
  - hero feature
  - category chips
  - recipe cards
  - chef spotlight
  - newsletter section
- Rationale: Inclusive UX and discoverability.

## 8) Testing Strategy

- Model tests:
  - slug auto-generation
  - publish timestamp set on status change
  - `get_absolute_url` behavior for unpublished posts
  - profile defaults and string representation
- View tests:
  - list pagination
  - detail 404 for drafts
  - create/update/delete auth and redirects
  - comment creation flow
  - profile page rendering
- Form tests:
  - `PostForm` slug and validation logic
  - `CommentForm` validation
  - profile form validation
- Test organization:
  - add `apps/blog/tests/` with `__init__.py`
  - keep legacy `tests.py` if needed
  - use `get_user_model()`
  - create helpers or factories for users, posts, categories, and profiles
- CI support:
  - ensure `SECRET_KEY` and `DEBUG` are set for tests via `.env` or env vars
- Rationale: Regression prevention and safe refactoring.

## 9) CI/CD and Quality Tooling

- GitHub Actions workflow:
  - install deps
  - create `.env`
  - run migrations
  - run tests
  - run `collectstatic` in a safe way
  - cache pip/npm where possible
- Pre-commit hooks:
  - black
  - isort
  - flake8
  - django-upgrades
- Optional typing:
  - mypy with django-stubs for app code
- Coverage:
  - generate report and enforce a minimum threshold if adopted
- Rationale: Consistency, quality, and faster reviews.

## 10) Admin Enhancements

- Register `Category`, `Post`, and `Comment` with `list_display` and `search_fields`.
- Use `list_filter` for status and category.
- Add `readonly_fields` for publish and created_at.
- Add inlines for comments under post admin.
- Add actions to publish or unpublish selected recipes.
- Consider profile/admin visibility for author bios or profile pictures if editorial workflow needs it.
- Rationale: Efficient editorial workflows.

## 11) Performance and Caching

- Confirm indices and add where needed based on query plans, especially for `(status, -publish)` and `slug`.
- Standardize pagination size and document it.
- Cache the recipe list page or fragments on non-personalized routes.
- Use Silk in `DEBUG` to profile hotspots.
- Consider image optimization and lazy-loading for recipe cards and profile images.
- Rationale: Sustained responsiveness under traffic.

## 12) Documentation and Developer Experience

- Update `README.md` with setup, `.env`, running tests, and Tailwind workflow.
- Keep `docs/guidelines.md` synchronized with actual test discovery and CI requirements.
- Add `CONTRIBUTING.md` with branch strategy, commit conventions, and review checklist.
- Add `Makefile` or `justfile` for common commands:
  - runserver
  - migrate
  - test
  - lint
  - format
  - tailwind-dev
- Pin Python and Node versions for reproducibility.
- Optional: dotenv loading in `manage.py` to ease local runs, documented clearly.
- Rationale: Faster onboarding and fewer environment mismatches.

## 13) Phased Roadmap

- Phase 0 — Pre-flight: add `.env.example`; document setup.
- Phase 1 — Config and Security: env-driven settings, security headers, logging, WhiteNoise.
- Phase 2 — Models and URLs: `get_absolute_url` implementations and guards, slug/timestamps, URL naming, category routes.
- Phase 3 — Views and Forms: access controls, delete POST flow, redirects/messages, pagination simplification, comment flow, send_mail safety, profile forms.
- Phase 4 — Templates: accessibility, SEO, timezone correctness, placeholder removal, recipe-focused homepage polish, profile page design.
- Phase 5 — Tests: model/view/form coverage; helpers/factories; restructure tests.
- Phase 6 — CI and Quality: GitHub Actions, pre-commit, coverage, optional typing.
- Phase 7 — Admin and Performance: admin polish, indices, caching, Silk profiling.
- Phase 8 — Docs and DX: README, CONTRIBUTING, Makefile/justfile, version pinning.

## 14) Open Questions and Assumptions

- The canonical requirements document (`docs/requirements.md`) is missing. This plan assumes the intent reflected in `docs/tasks.md`, `docs/guidelines.md`, and the current recipe-sharing UI.
- Should recipes eventually include structured ingredient and instruction models, or remain as rich text content?
- Are comments moderated or immediately public? This affects workflow and permissions.
- Is rich text allowed in recipes and comments? If yes, sanitization and/or a WYSIWYG strategy is needed.
- Should users be able to save/favorite recipes, rate them, or follow chefs/authors?
- Are profile avatars editable by users, and should they be stored in `media/profile_pics/`?
- Internationalization requirements may require additional tasks if needed.

## 15) Traceability to Source Tasks

- This plan covers items 1–60 from `docs/tasks.md`, grouped by theme; see sections 2–12 for the mapping.
- Where alternatives exist, the chosen option is annotated with rationale and the alternative is noted.
- Additional recipe-sharing and profile-related goals were added to match the current design direction in `templates/index.html`.

---

Maintenance: Keep this plan updated as decisions are made, especially around recipe structure, profile features, and community interactions. Once `docs/requirements.md` becomes available, reconcile any discrepancies and update priorities accordingly.