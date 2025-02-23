from django.urls import path

from . import views

app_name = "blog"

urlpatterns = [
    path("", views.post_list, name="post-list"),
    path("create/", views.post_create, name="post-create"),
    path(
        "<int:year>/<int:month>/<int:day>/<slug:post>/",
        views.post_detail,
        name="post-detail",
    ),
    path("<int:post_id>/update/", views.post_update, name="post-update"),
    path("<int:post_id>/delete/", views.post_delete, name="post-delete"),
]
