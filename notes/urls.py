from django.urls import path

from . import views

urlpatterns = [
    path("", views.NoteListView.as_view(), name="notes"),
    path("new/", views.NoteCreateView.as_view(), name="note_create"),
    path("<int:pk>/", views.NoteDetailView.as_view(), name="note_detail"),
    path("<int:pk>/edit/", views.NoteUpdateView.as_view(), name="note_edit"),
    path("<int:pk>/delete/", views.NoteDeleteView.as_view(), name="note_delete"),
]
