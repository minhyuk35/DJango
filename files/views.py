from __future__ import annotations

from django.contrib.admin.views.decorators import staff_member_required
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from .models import Upload


@staff_member_required(login_url="/admin/login/")
def index(request: HttpRequest) -> HttpResponse:
    uploads = Upload.objects.order_by("-created_at")[:200]
    return render(request, "files/index.html", {"uploads": uploads})


@staff_member_required(login_url="/admin/login/")
@require_POST
def upload_image(request: HttpRequest) -> JsonResponse:
    f = request.FILES.get("image")
    if not f:
        return JsonResponse({"error": "missing file"}, status=400)

    upload = Upload.objects.create(
        file=f,
        original_name=getattr(f, "name", "") or "",
        content_type=getattr(f, "content_type", "") or "",
        size=getattr(f, "size", 0) or 0,
    )
    return JsonResponse({"url": upload.file.url, "id": upload.pk})


@staff_member_required(login_url="/admin/login/")
@require_POST
def delete(request: HttpRequest, pk: int) -> HttpResponse:
    upload = get_object_or_404(Upload, pk=pk)
    upload.file.delete(save=False)
    upload.delete()
    return redirect("files_index")

