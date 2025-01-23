from django.contrib import admin

from .models import Customuser


# Register your models here.
@admin.register(Customuser)
class CustomUserAdmin(admin.ModelAdmin):
    list_display = ["email", "username", "is_staff", "is_superuser", "is_active"]
