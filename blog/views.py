from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.http import HttpRequest
from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic import CreateView, DeleteView, DetailView, ListView, UpdateView

from notes.models import Category, Note
from config.related import LinkItem, jaccard, tokens, url_for
from learning.models import Quiz

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
            queryset = queryset.order_by("title", "-created_at")
        else:
            queryset = queryset.order_by("-created_at")
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


class BlogPostDetailView(DetailView):
    model = Post
    template_name = "blog/post_detail.html"
    context_object_name = "post"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        post: Post = context["post"]

        quiz = Quiz.objects.filter(content_type__model="post", object_id=post.pk).prefetch_related("questions").first()
        context["quiz"] = quiz

        base_tokens = tokens(post.title + " " + (post.content or ""))
        candidates: list[Post | Note] = list(
            Post.objects.exclude(pk=post.pk).only("id", "title", "content", "created_at").order_by("-created_at")[:80]
        ) + list(Note.objects.only("id", "title", "content", "updated_at", "created_at").order_by("-updated_at")[:80])

        scored: list[tuple[float, Post | Note]] = []
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

        cat_slugs = list(post.categories.values_list("slug", flat=True))
        timeline: list[LinkItem] = []
        if cat_slugs:
            posts = (
                Post.objects.filter(categories__slug__in=cat_slugs)
                .only("id", "title", "created_at")
                .distinct()
            )
            notes = (
                Note.objects.filter(categories__slug__in=cat_slugs)
                .only("id", "title", "updated_at", "created_at")
                .distinct()
            )
            for p in posts:
                timeline.append(LinkItem(kind="post", title=p.title, date=p.created_at, url=url_for(p)))
            for n in notes:
                timeline.append(LinkItem(kind="note", title=n.title, date=n.updated_at, url=url_for(n)))
            timeline.sort(key=lambda x: x.date, reverse=True)
            timeline = timeline[:20]

        context["related_items"] = related
        context["timeline_items"] = timeline
        return context


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
