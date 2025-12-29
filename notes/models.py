from django.db import models
from django.utils.text import slugify


class Category(models.Model):
    name = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(max_length=60, unique=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["name"]

    def __str__(self) -> str:
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            base = slugify(self.name) or "category"
            candidate = base
            suffix = 2
            while Category.objects.filter(slug=candidate).exclude(pk=self.pk).exists():
                candidate = f"{base}-{suffix}"
                suffix += 1
            self.slug = candidate
        super().save(*args, **kwargs)


class Note(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField(blank=True)
    categories = models.ManyToManyField(Category, related_name="notes", blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return self.title
