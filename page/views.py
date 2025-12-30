from django.shortcuts import get_object_or_404, render

from .models import AboutProfile, PortfolioItem

def about(request):
    profile, _ = AboutProfile.objects.get_or_create(pk=1)
    if request.user.is_staff:
        portfolio_items = PortfolioItem.objects.all()
    else:
        portfolio_items = PortfolioItem.objects.filter(is_published=True)
    return render(
        request,
        "page/about.html",
        {"profile": profile, "portfolio_items": portfolio_items},
    )

def portfolio_detail(request, pk: int):
    if request.user.is_staff:
        item = get_object_or_404(PortfolioItem, pk=pk)
    else:
        item = get_object_or_404(PortfolioItem, pk=pk, is_published=True)
    return render(request, "page/portfolio_detail.html", {"item": item})

def contact(request):
    return render(request, "page/contact.html")

