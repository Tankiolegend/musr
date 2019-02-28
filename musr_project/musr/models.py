# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from django.contrib.auth.models import User

# Create your models here.

# Profile Model
class Profile(models.Model):
    # link to django user model
    user = models.OneToOneField(User, primary_key=True, on_delete=models.CASCADE)

    # store user image
    picture = models.ImageField(upload_to="profile_images", blank=True)

    def __str__(self):
        return self.user.username


class Following(models.Model):
    # create two foreign keys from profile, one a follower and the other the followed
    follower = models.ForeignKey(
        Profile, on_delete=models.CASCADE, related_name="follower"
    )

    followee = models.ForeignKey(
        Profile, on_delete=models.CASCADE, related_name="followee"
    )

    # set the pair to function as a multi attribute primary key
    class Meta:
        unique_together = (("follower", "followee"),)
        verbose_name_plural = "following"


class Post(models.Model):
    # create a post ID as the post primary key
    Post_Id = models.AutoField(primary_key=True)

    # store Profile ID of poster
    poster = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name="poster")

    # a foreign key field if the post is reposted
    Original_Poster_Id = models.ForeignKey(
        Profile, null=True, on_delete=models.SET_NULL, related_name="original_poster"
    )

    # a field for the song's Deezr ID
    Song_Id = models.IntegerField()

    # a field for the date the post was made
    date = models.DateField()
