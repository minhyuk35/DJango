from __future__ import annotations

from dataclasses import dataclass

from django.db.models import Q
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render

from blog.models import Post
from notes.models import Note


@dataclass(frozen=True)
class SearchItem:
    kind: str  # "post" | "note"
    title: str
    date: object
    url: str


def search(request: HttpRequest) -> HttpResponse:
    query = (request.GET.get("q") or "").strip()

    posts = []
    notes = []
    if query:
        posts = (
            Post.objects.filter(Q(title__icontains=query))
            .only("id", "title", "created_at")
            .order_by("-created_at")[:50]
        )
        notes = (
            Note.objects.filter(Q(title__icontains=query))
            .only("id", "title", "updated_at", "created_at")
            .order_by("-updated_at", "-created_at")[:50]
        )

    context = {
        "query": query,
        "posts": posts,
        "notes": notes,
    }
    return render(request, "blog/search.html", context)

