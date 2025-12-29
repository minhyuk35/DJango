from django.contrib import admin

from .models import Category, Note


@admin.register(Note)
class NoteAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "updated_at", "created_at")
    search_fields = ("title", "content")
    ordering = ("-updated_at", "-created_at")


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "slug", "created_at")
    search_fields = ("name", "slug")
    ordering = ("name",)
