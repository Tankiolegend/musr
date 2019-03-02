from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import HttpResponse
from django.shortcuts import redirect

from .models import Profile, Post, Following

# Index view (Whats hot)
def whats_hot(request):
    return render(request, "musr/whats_hot.html", {})


# Profile views (including redirect to own)
@login_required
def own_profile(request):
    return redirect("profile", username=request.user.username)


def profile(request, username):
    user = User.objects.get(username=username)
    profile = Profile.objects.get(user=user)
    profilePosts = Post.objects.filter(poster=profile).order_by("-date")
    return render(request, "musr/profile.html", {"posts": profilePosts})


# Feed view
@login_required
def feed(request):
    return render(request, "musr/feed.html", {})


# Add post!
@login_required
def add_post(request):
    if request.method != "POST":
        return redirect("/")

    # TODO: validate this data!!!! this is begging for mysql injection
    song_id = request.POST["song"]
    profile = Profile.objects.get(user=request.user)

    newpost = Post.objects.create(poster=profile, song_id=song_id)

    return HttpResponse("OK")


# Account photo upload
@login_required
def photo_upload(request):
    user = request.user
    profile, created = Profile.objects.get_or_create(user=user)

    if request.method == "POST":
        if profile and "photoUpload" in request.FILES:
            profile.picture = request.FILES["photoUpload"]
            profile.save()

    return render(request, "musr/photo-upload.html", {"profile": profile})
