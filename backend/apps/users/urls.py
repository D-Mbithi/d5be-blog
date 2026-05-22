from django.urls import path
from .views import profielview

app_name = "users"


urlpatterns = [
    path('<int:profile_id>/profile/', profielview, name="profile" )
]