from django.contrib import admin

from apps.blog.models import Category, Recipe  # type: ignore

# Register your models here.


@admin.register(Recipe)
class PostAdmin(admin.ModelAdmin):
    list_display = [
        "title",
        "slug",
        "author",
        "category",
        "publish",
        "status",
    ]
    list_filter = ["status", "publish", "author", "category"]
    search_fields = ["title"]
    prepopulated_fields = {"slug": ["title"]}
    raw_id_fields = ["author"]
    date_hierarchy = "publish"
    ordering = ["status", "publish"]
    show_facets = admin.ShowFacets.ALWAYS  # type: ignore


@admin.register(Category)  # type: ignore
class Category(admin.ModelAdmin):
    pass
