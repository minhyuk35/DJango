from django.db import models


class Upload(models.Model):
    file = models.FileField(upload_to="uploads/%Y/%m/")
    original_name = models.CharField(max_length=255, blank=True)
    content_type = models.CharField(max_length=100, blank=True)
    size = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return self.original_name or self.file.name

