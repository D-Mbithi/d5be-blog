from django.contrib import admin

from apps.blog.models import Category, Post

# Register your models here.


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = [
        "title",
        "slug",
        "author",
        "category",
        "publish",
        "created_at",
        "updated",
        "status",
    ]
    list_filter = ["status", "created_at", "publish", "author", "category"]
    search_fields = ["title"]
    prepopulated_fields = {"slug": ["title"]}
    raw_id_fields = ["author"]
    date_hierarchy = "publish"
    ordering = ["status", "publish"]
    show_facets = admin.ShowFacets.ALWAYS


@admin.register(Category)
class Category(admin.ModelAdmin):
    pass
