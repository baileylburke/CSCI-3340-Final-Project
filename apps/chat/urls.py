from django.urls import path

from . import views

app_name = "chat"

urlpatterns = [
    # All the user's team rooms.
    path("", views.room_list, name="rooms"),

    # Create a new room.
    path("new/", views.room_create, name="create"),

    # Open (or start) a direct message with a friend.
    path("dm/<int:user_id>/", views.start_dm, name="start_dm"),

    # One room's chat page.
    path("<int:room_id>/", views.room_detail, name="room"),

    # Post a message to a room.
    path("<int:room_id>/send/", views.send_message, name="send"),

    # Poll for new messages (JSON).
    path("<int:room_id>/messages/", views.messages_json, name="messages"),
]
