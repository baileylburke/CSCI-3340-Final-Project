from django.shortcuts import render, redirect
from django.contrib.auth import get_user_model, authenticate, login, logout

User = get_user_model()

# Import the friend request database model.
from .models import FriendRequest


def login_view(request):

    # Handle login form submission.
    if request.method == "POST":

        username = request.POST["username"]
        password = request.POST["password"]

        # Check the username and password.
        user = authenticate(
            username=username,
            password=password
        )

        # Log the user in if credentials are correct.
        if user is not None:
            login(request, user)
            return redirect("/")

        # Show an error if credentials are incorrect.
        else:
            return render(
                request,
                "accounts/login.html",
                {"error": "Invalid username or password."},
            )

    # Show the login page.
    return render(request, "accounts/login.html")


def register_view(request):

    # Handle registration form submission.
    if request.method == "POST":

        display_name = request.POST["display_name"]
        username = request.POST["username"]
        email = request.POST["email"]
        password = request.POST["password"]
        confirm_password = request.POST["confirm_password"]

        # Make sure both passwords match.
        if password != confirm_password:
            return render(
                request,
                "accounts/register.html",
                {"error": "Passwords do not match."},
            )

        # Make sure the username isn't already taken.
        if User.objects.filter(username=username).exists():
            return render(
                request,
                "accounts/register.html",
                {"error": "Username already exists."},
            )

        # Create the new user.
        User.objects.create_user(
            username=username,
            email=email,
            password=password,
            display_name=display_name,
        )

        # Send the user to login.
        return redirect("/login/")

    # Show the registration page.
    return render(request, "accounts/register.html")


def logout_view(request):

    # Log the user out.
    logout(request)

    # Return to the homepage.
    return redirect("/")


def find_people(request):

    # Start with no search results.
    users = []

    # Get the search text.
    search = request.GET.get("search", "").strip()

    # Handle an Add Friend request.
    if request.method == "POST":

        # Make sure the user is logged in.
        if not request.user.is_authenticated:
            return redirect("/login/")

        # Get the person we want to add.
        user_id = request.POST.get("user_id")

        # Find that person.
        person = User.objects.get(id=user_id)

        # Create the friend request.
        FriendRequest.objects.create(
            from_user=request.user,
            to_user=person,
        )

        # Return to the people page.
        return redirect("/people/")

    # Search if text was entered.
    if search:

        # Find matching usernames.
        users = User.objects.filter(
            username__icontains=search
        )

        # Don't show yourself.
        if request.user.is_authenticated:
            users = users.exclude(
                id=request.user.id
            )

    # Show the people page.
    return render(
        request,
        "accounts/people.html",
        {
            "users": users,
            "search": search,
        },
    )