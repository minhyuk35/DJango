from django.contrib import admin

from .models import Upload


@admin.register(Upload)
class UploadAdmin(admin.ModelAdmin):
    list_display = ("id", "original_name", "content_type", "size", "created_at")
    search_fields = ("original_name", "file")
    ordering = ("-created_at",)

