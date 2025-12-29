from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.http import HttpRequest
from django.urls import reverse_lazy
from django.views.generic import CreateView, DeleteView, DetailView, ListView, UpdateView

from .forms import NoteForm
from .models import Category, Note


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
    ordering = ["-updated_at", "-created_at"]

    def get_queryset(self):
        queryset = super().get_queryset().prefetch_related("categories")
        category_slug = self.request.GET.get("category")
        if category_slug:
            queryset = queryset.filter(categories__slug=category_slug)
        return queryset.distinct()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        category_slug = self.request.GET.get("category", "")
        if category_slug:
            context["selected_category"] = Category.objects.filter(slug=category_slug).first()
        else:
            context["selected_category"] = None
        return context


class NoteDetailView(DetailView):
    model = Note
    template_name = "notes/detail.html"
    context_object_name = "note"


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
