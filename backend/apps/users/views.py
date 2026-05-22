from django.shortcuts import render,get_object_or_404
from .models import Profile

# Create your views here.
def profielview(request, profile_id):
    profile = get_object_or_404(Profile, id=profile_id)
    return render(
        request,
        "account/profile.html",
        {"profile": profile},
    )