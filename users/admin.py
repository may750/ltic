from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import User


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (
        ("Rôle et profil", {"fields": ("role", "encadrant", "specialite", "competences", "cv", "service", "matricule")}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ("Rôle", {"fields": ("role",)}),
    )
    list_display = ("username", "email", "role", "is_staff")
    list_filter = ("role",)
# Register your models here.
