from django.shortcuts import render

def about(request):
    return render(request, "page/about.html")

def contact(request):
    return render(request, "page/contact.html")

