from django.contrib import admin

from .models import Quiz, QuizQuestion


class QuizQuestionInline(admin.TabularInline):
    model = QuizQuestion
    extra = 0


@admin.register(Quiz)
class QuizAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "content_type", "object_id", "updated_at")
    list_filter = ("content_type",)
    search_fields = ("title",)
    ordering = ("-updated_at",)
    inlines = [QuizQuestionInline]

