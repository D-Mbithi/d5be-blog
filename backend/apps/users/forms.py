from .models import CustomUser, Profile
from django import forms
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


class ProfileForm(forms.ModelForm):
    first_name = forms.CharField(max_length=30, required=False)
    last_name = forms.CharField(max_length=30, required=False)
    email = forms.EmailField(required=True)
    username = forms.CharField(max_length=150, required=True)

    class Meta:
        model = Profile
        fields = ('profile_pic', 'bio')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.user:
            self.fields['first_name'].initial = self.instance.user.first_name
            self.fields['last_name'].initial = self.instance.user.last_name
            self.fields['email'].initial = self.instance.user.email
            self.fields['username'].initial = self.instance.user.username

    def save(self, commit=True):
        profile = super().save(commit=False)
        if commit:
            user = profile.user
            user.first_name = self.cleaned_data['first_name']
            user.last_name = self.cleaned_data['last_name']
            user.email = self.cleaned_data['email']
            user.username = self.cleaned_data['username']
            user.save()
            profile.save()
        return profile