from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

from apps.blog import views

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", views.post_list, name="index"),
    path("accounts/", include("allauth.urls")),
    path("accounts/", include("apps.users.urls", namespace='accounts')),
    path("recipes/", include("apps.blog.urls", namespace="blog")),
]

urlpatterns += [
    path("silk/", include("silk.urls", namespace="silk")),
    path("__reload__/", include("django_browser_reload.urls")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)