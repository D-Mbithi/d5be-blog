from django.contrib import admin
from django.urls import include, path

from apps.blog import views

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", views.post_list, name="index"),
    path("accounts/", include("allauth.urls")),
    path("accounts/", include("apps.users.urls")),
    path("recipes/", include("apps.blog.urls", namespace="blog")),
]

urlpatterns += [path("silk/", include("silk.urls", namespace="silk"))]
