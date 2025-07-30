from django.core.mail import send_mail
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.shortcuts import get_object_or_404, render
from django.views.generic.list import ListView

from .forms import CategoryForm, PostForm, EmailPostForm
from .models import Post


# Create your views here.
class PostListView(ListView):
    queryset = Post.published.all()
    template_name = 'blog/post_list_class.html'
    paginate_by = 10
    context_object_name = 'posts'
def post_list(request):
    posts_list = Post.objects.filter(status="PB")

    paginator = Paginator(posts_list, 9)
    page = request.GET.get("page")
    try:
        posts = paginator.get_page(page)
    except PageNotAnInteger:
        posts = paginator.page(1)
    except EmptyPage:
        posts = paginator.page(paginator.num_pages)

    template = "blog/post_list.html"
    context = {"posts": posts}
    return render(request, template, context)


def post_detail(request, year, month, day, post):
    post = get_object_or_404(
        Post,
        slug=post,
        publish__year=year,
        publish__month=month,
        publish__day=day,
    )
    template = "blog/post_detail.html"
    context = {"post": post}
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

def post_share(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    sent = False

    if request.method == "POST":
        form = EmailPostForm(request.POST)
        if form.is_valid():
            # Process the form data
            cd = form.cleaned_data
            post_url = request.build_absolute_uri(post.get_absolute_url())
            subject = f"{cd['name']} ({cd['email']}) recommends you to read the following article { post.title }"
            message = f"Read {post.title} at {post_url}\n\n" f"{cd['name']}\'s comments: {cd['comments']}"

            send_mail(
                subject=subject,
                message=message,
                from_email=None,
                recipient_list=[cd['to']]
            )
            sent = True
    else:
        form = EmailPostForm()
    template = "blog/post_share.html"
    context = {
        "form": form,
        "post": post,
        "sent": sent,
    }
    return render(request, template, context)
