from django.shortcuts import render


def index(request):
    """Placeholder so the project runs immediately after setup."""
    return render(request, "home.html")
