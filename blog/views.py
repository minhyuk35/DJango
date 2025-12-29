from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.http import HttpRequest
from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic import CreateView, DeleteView, DetailView, ListView, UpdateView

from notes.models import Note

from .forms import PostForm
from .models import Post


class StaffOnlyMixin(LoginRequiredMixin, UserPassesTestMixin):
    login_url = "/admin/login/"
    request: HttpRequest

    def test_func(self) -> bool:
        user = self.request.user
        return bool(user and user.is_authenticated and user.is_staff)

def post_list(request):
    posts = Post.objects.all().order_by("-created_at")[:8]
    notes = Note.objects.all().order_by("-updated_at", "-created_at")[:8]
    return render(request, 'blog/main.html', {'posts': posts, 'notes': notes})


class BlogPostListView(ListView):
    model = Post
    template_name = "blog/post_list.html"
    context_object_name = "posts"
    ordering = ["-created_at"]


class BlogPostDetailView(DetailView):
    model = Post
    template_name = "blog/post_detail.html"
    context_object_name = "post"


class BlogPostCreateView(StaffOnlyMixin, CreateView):
    model = Post
    form_class = PostForm
    template_name = "blog/post_form.html"
    success_url = reverse_lazy("blog_post_list")


class BlogPostUpdateView(StaffOnlyMixin, UpdateView):
    model = Post
    form_class = PostForm
    template_name = "blog/post_form.html"
    success_url = reverse_lazy("blog_post_list")


class BlogPostDeleteView(StaffOnlyMixin, DeleteView):
    model = Post
    template_name = "blog/post_confirm_delete.html"
    success_url = reverse_lazy("blog_post_list")
