from django.urls import path

from . import views

app_name = "blog"

urlpatterns = [
    path("", views.PostListView.as_view(), name="post-list"),
    path("category/<int:pk>/", views.CategoryDetailView.as_view(), name="category-detail"),
]