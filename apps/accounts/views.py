from django.contrib.auth import login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.shortcuts import redirect, render
from django.views.decorators.http import require_POST

from .forms import RegisterForm


def login_view(request):
    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            login(request, form.get_user())
            return redirect("core:index")
    else:
        form = AuthenticationForm(request)

    return render(request, "accounts/login.html", {"form": form})


def register_view(request):
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("accounts:login")
    else:
        form = RegisterForm()

    return render(request, "accounts/register.html", {"form": form})


@require_POST
def logout_view(request):
    """POST only, so a stray link or image tag cannot end someone's session."""
    logout(request)
    return redirect("core:index")
