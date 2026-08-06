from django.shortcuts import render, redirect
from django.contrib.auth import get_user_model, authenticate, login, logout

User = get_user_model()


def login_view(request):

    if request.method == "POST":

        username = request.POST["username"]
        password = request.POST["password"]

        user = authenticate(
            username=username,
            password=password
        )

        if user is not None:
            login(request, user)
            return redirect("/")

        else:
            return render(
                request,
                "accounts/login.html",
                {"error": "Invalid username or password."},
            )

    return render(request, "accounts/login.html")


def register_view(request):

    if request.method == "POST":

        display_name = request.POST["display_name"]
        username = request.POST["username"]
        email = request.POST["email"]
        password = request.POST["password"]
        confirm_password = request.POST["confirm_password"]

        if password != confirm_password:
            return render(
                request,
                "accounts/register.html",
                {"error": "Passwords do not match."},
            )

        if User.objects.filter(username=username).exists():
            return render(
                request,
                "accounts/register.html",
                {"error": "Username already exists."},
            )

        User.objects.create_user(
            username=username,
            email=email,
            password=password,
            display_name=display_name,
        )

        return redirect("/login/")

    return render(request, "accounts/register.html")

def logout_view(request):
    logout(request)
    return redirect("/")