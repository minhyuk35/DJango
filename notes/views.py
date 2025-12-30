from __future__ import annotations

from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.http import HttpRequest
from django.urls import reverse_lazy
from django.views.generic import CreateView, DeleteView, DetailView, ListView, UpdateView
from typing import TYPE_CHECKING

from .forms import NoteForm
from .models import Category, Note
from config.related import LinkItem, jaccard, tokens, url_for
from learning.models import Quiz

if TYPE_CHECKING:
    from blog.models import Post


class StaffOnlyMixin(LoginRequiredMixin, UserPassesTestMixin):
    login_url = "/admin/login/"
    request: HttpRequest

    def test_func(self) -> bool:
        user = self.request.user
        return bool(user and user.is_authenticated and user.is_staff)


class NoteListView(ListView):
    model = Note
    template_name = "notes/index.html"
    context_object_name = "notes"
    paginate_by = 12

    def get_queryset(self):
        queryset = super().get_queryset().prefetch_related("categories")
        category_slug = self.request.GET.get("category")
        if category_slug:
            queryset = queryset.filter(categories__slug=category_slug)

        sort_key = self.request.GET.get("sort") or "recent"
        if sort_key == "old":
            queryset = queryset.order_by("created_at")
        elif sort_key == "title":
            queryset = queryset.order_by("title", "-updated_at")
        else:
            queryset = queryset.order_by("-updated_at", "-created_at")
        return queryset.distinct()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        category_slug = self.request.GET.get("category", "")
        if category_slug:
            context["selected_category"] = Category.objects.filter(slug=category_slug).first()
        else:
            context["selected_category"] = None
        context["sort"] = self.request.GET.get("sort") or "recent"
        return context


class NoteDetailView(DetailView):
    model = Note
    template_name = "notes/detail.html"
    context_object_name = "note"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        note: Note = context["note"]

        quiz = Quiz.objects.filter(content_type__model="note", object_id=note.pk).prefetch_related("questions").first()
        context["quiz"] = quiz

        base_tokens = tokens(note.title + " " + (note.content or ""))
        from blog.models import Post

        candidates: list[Note | Post] = list(
            Note.objects.exclude(pk=note.pk).only("id", "title", "content", "updated_at", "created_at").order_by("-updated_at")[:80]
        )
        candidates += list(Post.objects.only("id", "title", "content", "created_at").order_by("-created_at")[:80])

        scored: list[tuple[float, Note | Post]] = []
        for c in candidates:
            score = jaccard(base_tokens, tokens(c.title + " " + (c.content or "")))
            if score > 0:
                scored.append((score, c))
        scored.sort(key=lambda x: x[0], reverse=True)

        related: list[LinkItem] = []
        for score, obj in scored[:6]:
            related.append(
                LinkItem(
                    kind="post" if isinstance(obj, Post) else "note",
                    title=obj.title,
                    date=obj.created_at if isinstance(obj, Post) else obj.updated_at,
                    url=url_for(obj),
                )
            )

        cat_slugs = list(note.categories.values_list("slug", flat=True))
        timeline: list[LinkItem] = []
        if cat_slugs:
            notes = (
                Note.objects.filter(categories__slug__in=cat_slugs)
                .only("id", "title", "updated_at", "created_at")
                .distinct()
            )
            posts = (
                Post.objects.filter(categories__slug__in=cat_slugs)
                .only("id", "title", "created_at")
                .distinct()
            )
            for n in notes:
                timeline.append(LinkItem(kind="note", title=n.title, date=n.updated_at, url=url_for(n)))
            for p in posts:
                timeline.append(LinkItem(kind="post", title=p.title, date=p.created_at, url=url_for(p)))
            timeline.sort(key=lambda x: x.date, reverse=True)
            timeline = timeline[:20]

        context["related_items"] = related
        context["timeline_items"] = timeline
        return context


class NoteCreateView(StaffOnlyMixin, CreateView):
    model = Note
    form_class = NoteForm
    template_name = "notes/form.html"
    success_url = reverse_lazy("notes")


class NoteUpdateView(StaffOnlyMixin, UpdateView):
    model = Note
    form_class = NoteForm
    template_name = "notes/form.html"
    success_url = reverse_lazy("notes")


class NoteDeleteView(StaffOnlyMixin, DeleteView):
    model = Note
    template_name = "notes/confirm_delete.html"
    success_url = reverse_lazy("notes")
