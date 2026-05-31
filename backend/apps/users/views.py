from django.shortcuts import render, get_object_or_404, redirect
from .models import Profile
from .forms import ProfileForm
from apps.blog.models import Recipe


# Create your views here.
def profile_view(request, profile_id):
    profile = get_object_or_404(Profile, id=profile_id)
    # recipes = Recipe.objects.filter(author=profile.user)
    # count = recipes.count()
    # saved_recipes = profile.saved_recipes.all()
    return render(
        request,
        "account/profile.html",
        {
            "profile": profile,
            # "recipes": recipes,
            # "count": count,
            # "saved_recipes": saved_recipes,
        },
    )

def edit_profile(request, profile_id):
    profile = get_object_or_404(Profile, id=profile_id)
    if request.method == "POST":
        form = ProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            return redirect("accounts:profile", profile_id=profile.id)
    else:
        form = ProfileForm(instance=profile)
    
    return render(
        request,
        "account/profile_edit.html",
        {"form": form, "profile": profile},
    )