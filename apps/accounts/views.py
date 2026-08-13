from django.contrib.auth import authenticate, get_user_model, login, logout
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from apps.core.models import notify

from .models import FriendRequest

User = get_user_model()


def login_view(request):

    # Handle login form submission.
    if request.method == "POST":

        username = request.POST.get("username", "")
        password = request.POST.get("password", "")

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

        display_name = request.POST.get("display_name", "")
        username = request.POST.get("username", "")
        email = request.POST.get("email", "")
        password = request.POST.get("password", "")
        confirm_password = request.POST.get("confirm_password", "")

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


@login_required
def find_people(request):

    # Handle an Add Friend request.
    if request.method == "POST":

        # Get the person we want to add.
        person = get_object_or_404(User, id=request.POST.get("user_id"))

        # Is there already a request between the two, either way around?
        already_linked = FriendRequest.objects.filter(
            Q(from_user=request.user, to_user=person)
            | Q(from_user=person, to_user=request.user)
        ).exists()

        # No friending yourself and no duplicate requests.
        if person != request.user and not already_linked:
            FriendRequest.objects.create(
                from_user=request.user,
                to_user=person,
            )
            notify(
                person,
                f"{request.user} sent you a friend request.",
                "/friend-requests/",
            )

        # Return to the people page, keeping the search.
        search = request.POST.get("search", "")
        return redirect(f"/people/?search={search}" if search else "/people/")

    # Get the search text.
    search = request.GET.get("search", "").strip()

    # Search if text was entered. Each result carries a status so the
    # template knows which button to show (Add / Pending / Friends).
    results = []
    if search:
        matches = (
            User.objects.filter(
                Q(username__icontains=search)
                | Q(display_name__icontains=search)
            )
            .exclude(id=request.user.id)
        )
        for person in matches:
            link = (
                FriendRequest.objects.filter(
                    Q(from_user=request.user, to_user=person)
                    | Q(from_user=person, to_user=request.user)
                )
                .first()
            )
            if link is None:
                status = "none"
            elif link.accepted:
                status = "friends"
            elif link.from_user_id == request.user.id:
                status = "sent"
            else:
                status = "received"
            results.append({"person": person, "status": status})

    # Show the people page with the user's current friends.
    return render(
        request,
        "accounts/people.html",
        {
            "results": results,
            "search": search,
            "friends": request.user.friends(),
        },
    )


@login_required
def friend_requests(request):

    # Get requests sent to the current user.
    requests = FriendRequest.objects.filter(
        to_user=request.user,
        accepted=False,
    ).select_related("from_user")

    # Requests the user has sent that are still waiting.
    sent = FriendRequest.objects.filter(
        from_user=request.user,
        accepted=False,
    ).select_related("to_user")

    # Show the friend requests page.
    return render(
        request,
        "accounts/friend_requests.html",
        {
            "requests": requests,
            "sent": sent,
        },
    )


@login_required
@require_POST
def accept_friend_request(request, request_id):

    # Find the friend request. Only the recipient can accept it.
    friend_request = get_object_or_404(
        FriendRequest,
        id=request_id,
        to_user=request.user,
        accepted=False,
    )

    # Mark the request as accepted.
    friend_request.accepted = True
    friend_request.save()

    # Let the sender know.
    notify(
        friend_request.from_user,
        f"{request.user} accepted your friend request.",
        "/people/",
    )

    # Return to friend requests.
    return redirect("/friend-requests/")


@login_required
@require_POST
def decline_friend_request(request, request_id):

    # Find the friend request. Only the recipient can decline it.
    friend_request = get_object_or_404(
        FriendRequest,
        id=request_id,
        to_user=request.user,
        accepted=False,
    )

    # Declining just deletes the request.
    friend_request.delete()

    # Return to friend requests.
    return redirect("/friend-requests/")
