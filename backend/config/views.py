from django.shortcuts import get_list_or_404, render
from apps.blog.models import Category, Recipe


def index(request):
    posts = Recipe.objects.all().order_by("-published")
    categories = get_list_or_404(Category)
    template = "index.html"
    context = {"posts": posts, "categories": categories}

    return render(request, template, context)
