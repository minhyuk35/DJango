from django.db import models
from django.utils import timezone

class Post(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField()
    categories = models.ManyToManyField("notes.Category", related_name="posts", blank=True)
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.title
