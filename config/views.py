from __future__ import annotations

from django.db.models import Q
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render
from django.utils.html import escape, strip_tags

from blog.models import Post
from notes.models import Note
from notes.models import Category
from django.db.models import Count
from django.db.models.functions import TruncDate
from django.http import JsonResponse
from django.utils import timezone
from datetime import timedelta

from metrics.models import DailyVisit


def _highlight(text: str, query: str) -> str:
    if not text:
        return ""
    if not query:
        return escape(text)

    lowered = text.lower()
    q = query.lower()
    start = lowered.find(q)
    if start < 0:
        return escape(text)
    end = start + len(query)
    return (
        escape(text[:start])
        + '<mark class="hl">'
        + escape(text[start:end])
        + "</mark>"
        + escape(text[end:])
    )


def _excerpt(text: str, query: str, radius: int = 70) -> str:
    plain = strip_tags(text or "")
    if not plain:
        return ""
    if not query:
        return escape(plain[: radius * 2])

    lowered = plain.lower()
    q = query.lower()
    idx = lowered.find(q)
    if idx < 0:
        return escape(plain[: radius * 2])
    start = max(0, idx - radius)
    end = min(len(plain), idx + len(query) + radius)
    prefix = "…" if start > 0 else ""
    suffix = "…" if end < len(plain) else ""
    snippet = plain[start:end]
    return prefix + _highlight(snippet, query) + suffix


def search(request: HttpRequest) -> HttpResponse:
    query = (request.GET.get("q") or "").strip()

    post_results: list[dict] = []
    note_results: list[dict] = []
    if query:
        posts = (
            Post.objects.filter(Q(title__icontains=query) | Q(content__icontains=query))
            .only("id", "title", "content", "created_at")
            .order_by("-created_at")[:50]
        )
        notes = (
            Note.objects.filter(Q(title__icontains=query) | Q(content__icontains=query))
            .only("id", "title", "content", "updated_at", "created_at")
            .order_by("-updated_at", "-created_at")[:50]
        )

        post_results = [
            {
                "pk": p.pk,
                "title_html": _highlight(p.title, query),
                "snippet_html": _excerpt(p.content, query),
                "date": p.created_at,
            }
            for p in posts
        ]
        note_results = [
            {
                "pk": n.pk,
                "title_html": _highlight(n.title, query),
                "snippet_html": _excerpt(n.content, query),
                "date": n.updated_at,
            }
            for n in notes
        ]

    context = {
        "query": query,
        "post_results": post_results,
        "note_results": note_results,
    }
    return render(request, "blog/search.html", context)


def garden_data(request: HttpRequest) -> JsonResponse:
    days = 180
    start = timezone.now().date() - timedelta(days=days - 1)

    post_daily = (
        Post.objects.filter(created_at__date__gte=start)
        .annotate(day=TruncDate("created_at"))
        .values("day")
        .annotate(count=Count("id"))
    )
    note_daily = (
        Note.objects.filter(created_at__date__gte=start)
        .annotate(day=TruncDate("created_at"))
        .values("day")
        .annotate(count=Count("id"))
    )

    daily_map: dict[str, int] = {}
    for row in post_daily:
        daily_map[str(row["day"])] = daily_map.get(str(row["day"]), 0) + int(row["count"])
    for row in note_daily:
        daily_map[str(row["day"])] = daily_map.get(str(row["day"]), 0) + int(row["count"])

    daily = []
    for i in range(days):
        d = start + timedelta(days=i)
        daily.append({"date": str(d), "count": daily_map.get(str(d), 0)})

    visits_qs = DailyVisit.objects.filter(date__gte=start).values("date", "count")
    visits_map: dict[str, int] = {str(row["date"]): int(row["count"]) for row in visits_qs}
    visits = []
    for i in range(days):
        d = start + timedelta(days=i)
        visits.append({"date": str(d), "count": visits_map.get(str(d), 0)})

    categories = (
        Category.objects.annotate(
            post_count=Count("posts", distinct=True),
            note_count=Count("notes", distinct=True),
        )
        .values("name", "slug", "post_count", "note_count")
        .order_by("name")
    )

    return JsonResponse({"days": days, "daily": daily, "visits": visits, "categories": list(categories)})
