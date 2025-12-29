from django.urls import reverse

from blog.models import Post

from .models import Category, Note


def notes_sidebar(request):
    categories = Category.objects.order_by("name")
    recent_notes = (
        Note.objects.order_by("-updated_at", "-created_at").only("id", "title", "content", "updated_at")[:5]
    )
    recent_posts = Post.objects.order_by("-created_at").only("id", "title", "content", "created_at")[:5]

    items = []
    for n in recent_notes:
        items.append(
            {
                "kind": "note",
                "title": n.title,
                "content": n.content,
                "timestamp": n.updated_at,
                "url": reverse("note_detail", args=[n.pk]),
            }
        )
    for p in recent_posts:
        items.append(
            {
                "kind": "post",
                "title": p.title,
                "content": p.content,
                "timestamp": p.created_at,
                "url": reverse("blog_post_detail", args=[p.pk]),
            }
        )
    items.sort(key=lambda x: x["timestamp"], reverse=True)
    recent_items = items[:8]
    return {
        "notes_categories": categories,
        "recent_notes": recent_notes,
        "recent_posts": recent_posts,
        "recent_items": recent_items,
    }
