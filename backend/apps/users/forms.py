from .models import CustomUser
from django.contrib.auth.forms import UserCreationForm, UserChangeForm


class CustomUserCreationForm(UserCreationForm):
    # pyrefly: ignore [bad-override]
    class Meta:
        model = CustomUser
        fields = ('email',"username")

class CustomUserChangeForm(UserChangeForm):
    # pyrefly: ignore [bad-override]
    class Meta:
        model = CustomUser
        fields = ('email',"username")