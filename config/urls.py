from django.contrib import admin
from django.urls import include, path
from django.views.generic.base import TemplateView

from apps.blog import views

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", views.post_list, name="index"),
    path("blog/", include("apps.blog.urls", namespace="blog")),
    path('', include('admin_soft.urls')),
]

urlpatterns += [path("silk/", include("silk.urls", namespace="silk"))]
