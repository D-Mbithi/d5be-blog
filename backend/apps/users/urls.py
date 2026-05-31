from django.urls import path
from .views import profile_view, edit_profile

app_name = "accounts"


urlpatterns = [
    path('profile/<int:profile_id>/', profile_view, name="profile" ),
    path('profile/<int:profile_id>/edit/', edit_profile, name="edit_profile" )
]