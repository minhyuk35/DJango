from django.urls import path

from . import views

urlpatterns = [
    path("", views.BlogPostListView.as_view(), name="blog_post_list"),
    path("new/", views.BlogPostCreateView.as_view(), name="blog_post_create"),
    path("<int:pk>/", views.BlogPostDetailView.as_view(), name="blog_post_detail"),
    path("<int:pk>/edit/", views.BlogPostUpdateView.as_view(), name="blog_post_edit"),
    path("<int:pk>/delete/", views.BlogPostDeleteView.as_view(), name="blog_post_delete"),
]

