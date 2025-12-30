from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="files_index"),
    path("upload-image/", views.upload_image, name="files_upload_image"),
    path("<int:pk>/delete/", views.delete, name="files_delete"),
]

