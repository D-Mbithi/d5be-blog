from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .forms import CustomUserCreationForm, CustomUserChangeForm
from .models import CustomUser, Profile


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm
    model = CustomUser
    list_display = ('id', 'email', 'is_staff', 'is_active')
    list_filter = ('email', 'is_staff', 'is_active')



@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user','created', 'modified')
