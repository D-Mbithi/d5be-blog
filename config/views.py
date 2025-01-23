from django.shortcuts import get_list_or_404, render

from apps.blog.models import Category, Post


def index(request):
    posts = get_list_or_404(Post)
    categories = get_list_or_404(Category)
    template = "index.html"
    context = {"posts": posts, "categories": categories}

    return render(request, template, context)
