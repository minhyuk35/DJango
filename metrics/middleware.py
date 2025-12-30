from __future__ import annotations

from django.db import IntegrityError
from django.db.models import F
from django.utils import timezone

from .models import DailyVisit


class DailyVisitMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)

        if request.method not in {"GET", "HEAD"}:
            return response

        # Avoid counting internal assets / admin / APIs.
        path = request.path or ""
        if (
            path.startswith("/static/")
            or path.startswith("/media/")
            or path.startswith("/admin/")
            or path.startswith("/api/")
            or path == "/favicon.ico"
        ):
            return response

        # Avoid staff activity skewing public stats.
        user = getattr(request, "user", None)
        if getattr(user, "is_staff", False):
            return response

        today = timezone.localdate()

        # Concurrency-safe increment without locking.
        updated = DailyVisit.objects.filter(date=today).update(count=F("count") + 1)
        if updated:
            return response

        try:
            DailyVisit.objects.create(date=today, count=1)
        except IntegrityError:
            DailyVisit.objects.filter(date=today).update(count=F("count") + 1)

        return response

