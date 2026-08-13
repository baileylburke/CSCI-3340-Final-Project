from django.urls import path

from . import views


app_name = "accounts"


urlpatterns = [
    # Login page.
    path("login/", views.login_view, name="login"),

    # Account registration page.
    path("register/", views.register_view, name="register"),

    # Logs the user out and returns them to the homepage.
    path("logout/", views.logout_view, name="logout"),

    # Opens the page where users can search for other people.
    path("people/", views.find_people, name="find_people"),

    # Opens the page where users can search for other people.
    path("people/", views.find_people, name="find_people"),

    # Shows incoming friend requests.
    path("friend-requests/", views.friend_requests, name="friend_requests"),

    # Accepts a friend request.
    path(
         "friend-requests/<int:request_id>/accept/",
         views.accept_friend_request,
         name="accept_friend_request",
    ),

    
]