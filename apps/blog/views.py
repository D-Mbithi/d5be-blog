from django.shortcuts import get_object_or_404, render

from .forms import CategoryForm, PostForm
from .models import Post


# Create your views here.
def post_list(request):
    posts = Post.published.all()
    template = "blog/blog_list.html"
    context = {"posts": posts}
    return render(request, template, context)


def post_detail(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    template = "blog/post_detail.html"
    context = {
        "post": post
    }
    return render(request, template, context)


def post_create(request):
    if request.method == "POST":
        form = PostForm(request.POST)

        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
    else:
        form = PostForm()

    template = "blog/post_create.html"
    context = {"form": form}
    return render(request, template, context)


def post_update(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    if request.method == "POST":
        form = PostForm(request.POST, instance=post)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
    else:
        form = PostForm(instance=post)
    template = "blog/post_update.html"
    context = {"form": form}
    return render(request, template, context)


def post_delete(request, post_id):
    if request.method == "DELETE":
        post = get_object_or_404(Post, id=post_id)
        post.delete()


def category_create(request):
    if request.method == "POST":
        form = CategoryForm(request.POST)
        if form.is_valid():
            form.save()
    else:
        form = CategoryForm()
    template = "blog/category_create.html"
    context = {
        "form": form,
    }
    return render(request, template, context)
