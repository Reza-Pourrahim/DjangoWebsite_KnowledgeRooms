from django.shortcuts import render, redirect
from django.db.models import Q

from django.http import HttpResponse

from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth.decorators import login_required

from .models import Room, Topic, Message
from .forms import RoomForm


# rooms = [
#     {"id": 1, "name": "Backend: Python Developers"},
#     {"id": 2, "name": "Designers"},
#     {"id": 3, "name": "Frontend Developers"},
# ]


def loginPage(request):

    if request.user.is_authenticated:
        return redirect("home")

    if request.method == "POST":
        form = AuthenticationForm(request, request.POST)
        if form.is_valid():
            username = form.cleaned_data.get("username")
            password = form.cleaned_data.get("password")
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect("home")  # Redirect to home or desired page
    else:
        form = AuthenticationForm()
    return render(request, "base/login.html", {"form": form})


def registerPage(request):
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.username = user.username.lower()
            user.save()
            login(request, user)
            return redirect("home")  # Redirect to home or desired page
    else:
        form = UserCreationForm()
    return render(request, "base/register.html", {"form": form})


def logoutPage(request):
    logout(request)
    return redirect("login")  # Redirect to login


@login_required(login_url="login")
def home(request):
    q = request.GET.get("q") if request.GET.get("q") != None else ""

    rooms = Room.objects.filter(
        Q(topic__name__icontains=q)
        | Q(name__icontains=q)
        | Q(description__icontains=q)
        | Q(host__username__icontains=q)
    )
    topics = Topic.objects.all()
    # room_count = len(rooms)
    room_count = rooms.count()  # it seems it is faster than len()
    room_messages = Message.objects.filter(Q(room__topic__name__icontains=q))

    context = {
        "rooms": rooms,
        "topics": topics,
        "room_count": room_count,
        "room_messages": room_messages,
    }
    return render(request, "base/home.html", context)


def room(request, pk):
    room = Room.objects.get(id=pk)
    room_messages = room.message_set.all()
    participants = room.participants.all()

    if request.method == "POST":
        message = Message.objects.create(
            user=request.user, room=room, body=request.POST.get("body")
        )
        room.participants.add(request.user)
        return redirect("room", pk=room.id)

    context = {
        "room": room,
        "room_messages": room_messages,
        "participants": participants,
    }
    return render(request, "base/room.html", context)


@login_required(login_url="login")
def userProfile(request, pk):
    user = User.objects.get(id=pk)
    rooms = user.room_set.all()
    room_messages = user.message_set.all()
    topics = Topic.objects.all()
    context = {
        "user": user,
        "rooms": rooms,
        "room_messages": room_messages,
        "topics": topics,
    }
    return render(request, "base/profile.html", context)


@login_required(login_url="login")
def createRoom(request):
    if request.method == "POST":
        form = RoomForm(request.POST)  # pass data to the form
        if form.is_valid():
            room = form.save(commit=False)
            room.host = request.user
            room.save()
            return redirect("home")
    else:
        form = RoomForm()
    context = {"form": form}
    return render(request, "base/room_form.html", context)


@login_required(login_url="login")
def updateRoom(request, pk):
    room = Room.objects.get(id=pk)
    form = RoomForm(instance=room)

    if request.user != room.host:
        return HttpResponse("You are not allowed here!")

    if request.method == "POST":
        form = RoomForm(request.POST, instance=room)
        if form.is_valid():
            form.save()
            return redirect("home")
    context = {"form": form}
    return render(request, "base/room_form.html", context)


@login_required(login_url="login")
def deleteRoom(request, pk):
    room = Room.objects.get(id=pk)
    if request.user != room.host:
        return HttpResponse("You are not allowed here!")

    if request.method == "POST":
        room.delete()
        return redirect("home")

    context = {"obj": room}
    return render(request, "base/delete.html", context)


@login_required(login_url="login")
def deleteMessage(request, pk, room_id):
    msg = Message.objects.get(id=pk)
    if request.user != msg.user:
        return HttpResponse("You are not allowed here!")

    if request.method == "POST":
        msg.delete()
        return redirect("room", pk=room_id)

    context = {"obj": msg}
    return render(request, "base/delete.html", context)
