from __future__ import annotations

from django.db import models


class DailyVisit(models.Model):
    date = models.DateField(unique=True, db_index=True)
    count = models.PositiveIntegerField(default=0)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("-date",)

    def __str__(self) -> str:
        return f"{self.date}: {self.count}"

