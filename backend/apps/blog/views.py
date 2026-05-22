from django.core.mail import send_mail
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.contrib import messages
from django.http import Http404

# pyrefly: ignore [missing-import]
from .forms import CategoryForm, CommentForm, EmailPostForm, PostForm
# pyrefly: ignore [missing-import]
from .models import Post, Category


# Create your views here.
class PostListView(ListView):
    queryset = Post.published.all().select_related("author", "category")
    template_name = 'blog/post_list_class.html'
    paginate_by = 10
    context_object_name = 'posts'

class CategoryDetailView(DetailView):
    model = Category
    template_name = 'blog/category_detail.html'
    context_object_name = 'category'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['posts'] = self.object.posts.filter(status="PB").select_related("author", "category")
        return context


def post_list(request):
    posts_list = Post.objects.filter(status="PB").select_related("author", "category")

    paginator = Paginator(posts_list, 9)
    page_number = request.GET.get("page")
    posts = paginator.get_page(page_number)

    template = "index.html"
    context = {"posts": posts}
    return render(request, template, context)


def post_detail(request, year, month, day, post):
    post = get_object_or_404(
        Post.objects.select_related("author", "category"),
        slug=post,
        publish__year=year,
        publish__month=month,
        publish__day=day,
        status="PB",
    )
    comments = post.comments.filter(active=True)  # type: ignore
    form = CommentForm()
    template = "blog/post_detail.html"
    context = {
        "post": post, "form": form, "comments": comments,
        }  # type: ignore
    return render(request, template, context)


@login_required
def post_create(request):
    if request.method == "POST":
        form = PostForm(request.POST, request.FILES)

        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            messages.success(request, "Recipe created successfully.")
            if post.status == "PB" and post.publish:
                return redirect(post.get_absolute_url())
            return redirect('blog:post-list')
    else:
        form = PostForm()

    template = "blog/post_create.html"
    context = {"form": form}
    return render(request, template, context)


@login_required
def post_update(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    if post.author != request.user:
        raise Http404("You are not allowed to edit this post.")
        
    if request.method == "POST":
        form = PostForm(request.POST, request.FILES, instance=post)
        if form.is_valid():
            post = form.save(commit=False)
            post.save()
            messages.success(request, "Recipe updated successfully.")
            if post.status == "PB" and post.publish:
                return redirect(post.get_absolute_url())
            return redirect('blog:post-list')
    else:
        form = PostForm(instance=post)
    template = "blog/post_update.html"
    context = {"form": form}
    return render(request, template, context)


@login_required
@require_POST
def post_delete(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    if post.author != request.user:
        raise Http404("You are not allowed to delete this post.")
    post.delete()
    messages.success(request, "Recipe deleted successfully.")
    return redirect('blog:post-list')


@login_required
def category_create(request):
    if request.method == "POST":
        form = CategoryForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Category created successfully.")
            return redirect(reverse("blog:post-list"))
    else:
        form = CategoryForm()
    template = "blog/category_create.html"
    context = {
        "form": form,
    }
    return render(request, template, context)


def post_share(request, post_id):
    post = get_object_or_404(Post, id=post_id, status="PB")
    sent = False

    if request.method == "POST":
        form = EmailPostForm(request.POST)
        if form.is_valid():
            # Process the form data
            cd = form.cleaned_data
            post_url = request.build_absolute_uri(post.get_absolute_url())
            subject = (
                f"{cd['name']} ({cd['email']}) recommends you to read "
                f"the following article {post.title}"
            )  # type: ignore
            message = (
                f"Read {post.title} at {post_url}\n\n"
                f"{cd['name']}'s comments: {cd['comments']}"
            )  # type: ignore

            try:
                send_mail(
                    subject=subject,
                    message=message,
                    from_email=None,
                    recipient_list=[cd['to']]
                )
                sent = True
                messages.success(request, "Recipe shared successfully.")
            except Exception as e:
                messages.error(request, "There was an error sharing the recipe.")
    else:
        form = EmailPostForm()
    template = "blog/post_share.html"
    context = {
        "form": form,
        "post": post,
        "sent": sent,
    }
    return render(request, template, context)


@require_POST
def post_comment(request, post_id):
    post = get_object_or_404(Post, id=post_id, status="PB")
    form = CommentForm(request.POST)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.post = post
        comment.save()
        messages.success(request, "Comment added successfully.")

    if post.publish:
        return redirect(
            reverse(
                "blog:post-detail",
                args=[
                    post.publish.year,
                    post.publish.month,
                    post.publish.day,
                    post.slug
                ]
            ) + f"#comment-{comment.id}"
        )
    return redirect('blog:post-list')