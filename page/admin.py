from django.contrib import admin

from .models import AboutProfile, PortfolioItem


@admin.register(AboutProfile)
class AboutProfileAdmin(admin.ModelAdmin):
    fieldsets = ((None, {"fields": ("photo", "name", "university", "major")}),)

    def has_add_permission(self, request):
        return not AboutProfile.objects.exists()


@admin.register(PortfolioItem)
class PortfolioItemAdmin(admin.ModelAdmin):
    list_display = ("title", "is_published", "order", "updated_at")
    list_filter = ("is_published",)
    search_fields = ("title", "description", "link")
    ordering = ("order", "-created_at")
