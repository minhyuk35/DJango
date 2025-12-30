from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import datetime

from django.urls import reverse
from django.utils.html import strip_tags


_STOP = {
    "the",
    "a",
    "an",
    "and",
    "or",
    "of",
    "to",
    "in",
    "is",
    "are",
    "for",
    "with",
    "this",
    "that",
    "있다",
    "없는",
    "한다",
    "하기",
    "대한",
    "그리고",
    "또는",
    "에서",
    "으로",
}


def tokens(text: str) -> set[str]:
    plain = strip_tags(text or "").lower()
    raw = re.split(r"[^0-9A-Za-z가-힣]+", plain)
    return {t for t in raw if len(t) >= 2 and t not in _STOP}


def jaccard(a: set[str], b: set[str]) -> float:
    if not a or not b:
        return 0.0
    inter = len(a & b)
    union = len(a | b)
    return inter / union if union else 0.0


@dataclass(frozen=True)
class LinkItem:
    kind: str  # "post" | "note"
    title: str
    date: datetime
    url: str


def url_for(obj) -> str:
    if obj.__class__.__name__ == "Post":
        return reverse("blog_post_detail", args=[obj.pk])
    return reverse("note_detail", args=[obj.pk])
