"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from blog import views
from . import views as config_views
from django.conf import settings
from django.conf.urls.static import static
import os

urlpatterns = [
    path('admin/', admin.site.urls),
    path("search/", config_views.search, name="search"),
    path("api/garden/", config_views.garden_data, name="garden_data"),
    path("", include("page.urls")),
    path("blog/", include("blog.urls")),
    path("notes/", include("notes.urls")),
    path("files/", include("files.urls")),
    path("", views.post_list, name="post_list"),
]

if settings.DEBUG or os.environ.get("SERVE_MEDIA", "False") == "True":
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
