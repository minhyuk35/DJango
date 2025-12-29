from django.db import migrations
from django.utils.text import slugify


def _unique_slug(Category, base: str) -> str:
    base = base or "category"
    candidate = base
    suffix = 2
    while Category.objects.filter(slug=candidate).exists():
        candidate = f"{base}-{suffix}"
        suffix += 1
    return candidate


def seed_categories(apps, schema_editor):
    Category = apps.get_model("notes", "Category")
    # Fix any existing blank slugs (historical models don't run save()).
    for c in Category.objects.filter(slug=""):
        c.slug = _unique_slug(Category, slugify(c.name))
        c.save(update_fields=["slug"])

    for name in ["Django", "Python", "Linux", "Project"]:
        defaults = {"slug": _unique_slug(Category, slugify(name))}
        obj, created = Category.objects.get_or_create(name=name, defaults=defaults)
        if not created and not obj.slug:
            obj.slug = _unique_slug(Category, slugify(obj.name))
            obj.save(update_fields=["slug"])


def unseed_categories(apps, schema_editor):
    Category = apps.get_model("notes", "Category")
    Category.objects.filter(name__in=["Django", "Python", "Linux", "Project"]).delete()


class Migration(migrations.Migration):
    dependencies = [
        ("notes", "0002_category_note_categories"),
    ]

    operations = [
        migrations.RunPython(seed_categories, reverse_code=unseed_categories),
    ]
