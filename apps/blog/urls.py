from django.urls import path

from . import views

app_name = "blog"

urlpatterns = [
    path("", views.post_list, name="post-list"),
    path("<int:post_id>/", views.post_detail, name="post-detail"),
    path("<int:post_id>/update/", views.post_update, name="post-update"),
    path("create/", views.post_create, name="post-create"),
]
