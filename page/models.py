from django.db import models

class AboutProfile(models.Model):
    id = models.PositiveSmallIntegerField(primary_key=True, default=1, editable=False)
    photo = models.ImageField(upload_to="about/profile/", blank=True, null=True)
    name = models.CharField(max_length=100, blank=True)
    university = models.CharField(max_length=150, blank=True)
    major = models.CharField(max_length=150, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return "About Profile"


class PortfolioItem(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    link = models.URLField(max_length=500, blank=True)
    image = models.ImageField(upload_to="about/portfolio/", blank=True, null=True)
    order = models.PositiveIntegerField(default=0)
    is_published = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("order", "-created_at")

    def __str__(self) -> str:
        return self.title

    @property
    def description_one_line(self) -> str:
        if not self.description:
            return ""
        for line in str(self.description).splitlines():
            stripped = line.strip()
            if stripped:
                return stripped
        return ""
