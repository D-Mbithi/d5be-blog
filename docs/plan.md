# Project Improvement Plan

Date: 2025-08-10
Source basis: Intended source docs/requirements.md is missing. This plan is synthesized from the available authoritative materials in this repository: docs/tasks.md, project development guidelines (Junie/GUIDELINES and d5be-blog guidelines), and a light audit of the Django app structure. Open questions and assumptions are called out explicitly.

## 1) Key Goals and Constraints (Extracted from Available Sources)

- Configuration and deployment
  - Settings should be environment-driven via django-environ; a .env is required with at least SECRET_KEY and DEBUG.
  - Default DB is SQLite; migrations exist; tests run on ephemeral DB.
  - Tailwind is used for CSS; local npm workflow present.
  - Admin soft dashboard and django-silk enabled during development.
- Security posture
  - Avoid hard-coded DEBUG=True and ALLOWED_HOSTS=["*"]; support security headers in production.
  - Email backend default to console in dev; production-safe configuration required.
- Domain model and behavior
  - Blog with Post, Category, Comment; Post.save() sets publish timestamp on first publish.
  - Slug uniqueness relates to publish date (unique_for_date). created_at currently required.
- UX & templates
  - Accessible, SEO-friendly templates; correct timezone display; remove placeholders.
- Testing & CI
  - Tests should cover models, views, forms; CI should ensure .env is present and run collectstatic in dry run.
- Performance & admin
  - Reasonable indexes, consistent pagination, and optional caching; admin ergonomics.

## 2) Architecture & Configuration Improvements

1) Environment-driven settings
- Actions:
  - Read DEBUG via env.bool("DEBUG", default=False) and remove hard-coded True.
  - Replace ALLOWED_HOSTS=["*"] with env.list("ALLOWED_HOSTS", default=["127.0.0.1", "localhost"]).
  - Read EMAIL_BACKEND, CSRF_TRUSTED_ORIGINS, feature flags (e.g., ENABLE_SILK) from env.
- Rationale: Secure, reproducible deployments across environments; eliminate risky defaults.

2) Dev-only apps/middleware gating
- Actions:
  - Enable silk, django_extensions, django_seed only when DEBUG or explicit env flags are true.
- Rationale: Prevents leaking debugging/profiling tools in production.

3) Security headers & hardening (prod)
- Actions:
  - Configure SECURE_SSL_REDIRECT, SESSION_COOKIE_SECURE, CSRF_COOKIE_SECURE, SECURE_HSTS_SECONDS, SECURE_REFERRER_POLICY conditionally on DEBUG.
- Rationale: Aligns with Django security checklist for HTTPS deployments.

4) Static files in production
- Actions:
  - Add WhiteNoise middleware when not using external static server; verify collectstatic.
- Rationale: Simpler deployments; standards-based static file caching.

5) Logging
- Actions:
  - Configure LOGGING for request errors, security, and app logs. Console in DEBUG; structured/file option in production.
- Rationale: Operational visibility and incident response.

6) Caching
- Actions:
  - Default locmem cache in dev; allow Redis (via env) in production; cache template fragments for list pages.
- Rationale: Improves performance under load with minimal complexity.

7) .env.example
- Actions:
  - Provide sample with SECRET_KEY, DEBUG, ALLOWED_HOSTS, EMAIL_BACKEND, CSRF_TRUSTED_ORIGINS, ENABLE_SILK, CACHE_URL (optional), etc.
- Rationale: Developer onboarding and CI automation.

## 3) Data Model & Integrity

1) URL methods
- Actions:
  - Implement Category.get_absolute_url() to category listing route.
  - Update Comment.get_absolute_url() to point to an existing URL or remove the method to avoid reverse errors.
  - Guard Post.get_absolute_url() to raise ValueError if publish is None (or restrict usage to published posts in views/templates).
- Rationale: Prevent broken links and ensure consistent navigation.

2) Timestamps & slugging
- Actions:
  - Switch created_at to auto_now_add=True on Post and Comment, or if not feasible, ensure views set created_at explicitly before save.
  - Ensure slug is populated when missing (pre_save or save override) using slugify; respect unique_for_date constraint. If collision, append short suffix.
- Rationale: Reliable data defaults and user-friendly URLs.

3) Indices and constraints
- Actions:
  - Confirm existing index on -publish; consider composite index on (status, publish) and an index on slug.
- Rationale: Query speed for list/detail and filters.

4) Developer ergonomics
- Actions:
  - Ensure __str__ methods are informative (Category OK; Comment includes truncated body).
  - Audit related_name consistency (posts, comments) and document in model docstrings.
- Rationale: Admin usability and maintainability.

## 4) URLs & Navigation

- Standardize URL names to kebab-case (e.g., post-list); fix inconsistent aliases (e.g., postlist).
- Add category list/detail routes and templates; wire Category.get_absolute_url().
- If keeping Comment.get_absolute_url(), introduce a comment-detail route; otherwise remove the method.
- Provide an endpoint to create comments (dedicated POST or handled by post_detail with POST) with proper CSRF and redirects.
- Rationale: Predictable, RESTful routing and navigability.

## 5) Views & Controllers

- Protect create/update/delete views with @login_required and ownership/permissions checks.
- Convert delete handling to require_POST; add success redirect and messages; include CSRF in template.
- In create/update, redirect to get_absolute_url on success; use messages.success.
- Optimize list/detail queries with select_related('author', 'category') and prefetch_related('comments').
- Simplify pagination using Paginator.get_page().
- Wrap send_mail in post_share with error handling and optional throttling/CAPTCHA if public.
- Implement post_comment: validate CommentForm, set post relation, save, and redirect to the post detail with anchor.
- Ensure drafts are not exposed by detail view; return 404 for unauthorized/draft access.
- Rationale: Security, usability, and performance improvements.

## 6) Forms & Validation

- PostForm: include category and optional status; if created_at not auto, set in view.
- Slug handling in create view if not handled in model; avoid duplicates with suffix strategy.
- CategoryForm: clean_name to normalize whitespace; optional case-insensitive uniqueness check.
- CommentForm: enforce minimal length; consider HTML sanitization (bleach) if allowing rich text; otherwise rely on autoescape.
- Rationale: Data quality and safe inputs.

## 7) Templates, Accessibility, and SEO

- Replace hardcoded dates with publish|date and ensure timezone-aware display.
- Replace placeholder images with model fields or a sensible default static; always set alt text.
- Display non_field_errors and field.help_text; visibly style form errors.
- Add rel and aria attributes where appropriate; ensure color contrast (AA) and keyboard focus styles.
- Use {% url %} for category/author links; remove href="#" placeholders.
- Add SEO basics: title block, meta description, and canonical link on detail pages.
- Rationale: Inclusive UX and discoverability.

## 8) Testing Strategy

- Model tests: slug auto-generation, publish timestamp set on status change, get_absolute_url behavior for unpublished posts.
- View tests: list pagination, detail 404 for drafts, create/update/delete auth and redirects, comment creation flow.
- Form tests: PostForm slug/validation logic; CommentForm validation.
- Test organization: add apps/blog/tests/ with __init__.py; can retain legacy tests.py. Use get_user_model(); create helpers/factories.
- CI support: ensure SECRET_KEY and DEBUG are set for tests via .env in CI.
- Rationale: Regression prevention and safe refactoring.

## 9) CI/CD & Quality Tooling

- GitHub Actions workflow: install deps, create .env, run migrations, run tests, collectstatic --noinput (dry run ok), and cache pip/npm where possible.
- Pre-commit hooks: black, isort, flake8, django-upgrades.
- Optional typing: mypy with django-stubs for apps code.
- Coverage: generate report and enforce minimum (e.g., 80%).
- Rationale: Consistency, quality, and faster reviews.

## 10) Admin Enhancements

- Register Category, Post, Comment with list_display/search_fields; list_filter for status/category.
- Add readonly_fields for publish and created_at.
- Inline comments in the Post admin; bulk actions to publish/unpublish.
- Rationale: Efficient editorial workflows.

## 11) Performance & Caching

- Confirm indices and add where needed based on query plans ((status, -publish), slug).
- Standardize pagination size; document expectation for pages.
- Cache post list page or fragments when on non-personalized routes.
- Use Silk in DEBUG to profile hotspots.
- Rationale: Sustained responsiveness under traffic.

## 12) Documentation & Developer Experience (DX)

- Update README with setup, .env, running tests, Tailwind workflow; link to this plan and tasks.
- Keep .junie/guidelines.md synchronized with actual test discovery and CI.
- Add CONTRIBUTING.md with branch strategy, commit conventions, and review checklist.
- Add Makefile/justfile for common commands (runserver, migrate, test, lint, format, tailwind-dev).
- Pin Python/Node versions (.tool-versions/asdf or pyproject constraints) for reproducibility.
- Optional: dotenv loading in manage.py to ease local runs (documented opt-in).
- Rationale: Faster onboarding and fewer environment mismatches.

## 13) Phased Roadmap (Suggested Order)

- Phase 0 — Pre-flight: Add .env.example; document setup.
- Phase 1 — Config & Security: env-driven settings, security headers, logging, WhiteNoise.
- Phase 2 — Models & URLs: get_absolute_url implementations/guards, slug/timestamps, URL naming, category routes.
- Phase 3 — Views & Forms: access controls, delete POST flow, redirects/messages, pagination simplification, comment flow, send_mail safety.
- Phase 4 — Templates: accessibility, SEO, timezone correctness, placeholders removal.
- Phase 5 — Tests: model/view/form coverage; factories; restructure tests/.
- Phase 6 — CI/Quality: GitHub Actions, pre-commit, coverage, optional typing.
- Phase 7 — Admin & Performance: admin polish, indices, caching, Silk profiling.
- Phase 8 — Docs & DX: README, CONTRIBUTING, Makefile/justfile, version pinning.

## 14) Open Questions / Assumptions

- The canonical requirements document (docs/requirements.md) is currently missing. This plan assumes the intent reflected in docs/tasks.md and the project guidelines.
- Hosting target? (Heroku, Render, VPS, containerized) — this affects static file strategy and logging.
- Email provider and constraints? Rate limits and credentials influence post_share behavior and throttling.
- Are comments moderated or immediately public? This affects permissions and potential workflow/state on Comment.
- Is rich text allowed in comments/posts? If yes, we need sanitization and/or a WYSIWYG strategy.
- Internationalization requirements? If needed, add i18n/l10n tasks.

## 15) Traceability to Source Tasks

- This plan covers items 1–60 from docs/tasks.md, grouped by theme; see sections 2–12 for the mapping. Where alternatives exist (e.g., remove vs. add comment-detail), the chosen option is annotated with rationale and the alternative is noted.

---

Maintenance: Keep this plan updated as decisions are made (especially for open questions). Once docs/requirements.md becomes available, reconcile any discrepancies and update priorities accordingly.
