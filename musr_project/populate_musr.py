import os

import django
import datetime
import base64
import binascii
import functools
import hashlib
import importlib
import warnings

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "musr_project.settings")
django.setup()

from django.contrib.sites.models import Site
from musr.models import Profile, Following, Post, User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.conf import settings
from django.utils.module_loading import import_string
from django.utils.crypto import constant_time_compare, get_random_string, pbkdf2


def populate():
    setupAllAuth()

    musers = [
        {"user": "drake", "firstName": "Drake", "lastName": "Graham"},
        {"user": "beethoven", "firstName": "Ludwig", "lastName": "Beethoven"},
        {"user": "peterparker", "firstName": "Peter", "lastName": "Parker"},
        {"user": "michaelscott", "firstName": "Michael", "lastName": "Scott"},
        {"user": "postmalone", "firstName": "Austin", "lastName": "Malone"},
        {"user": "freddie", "firstName": "Freddie", "lastName": "Mercury"},
    ]

    followers = [
        {"follower": "Drake", "followee": "Beethoven"},
        {"follower": "Drake", "followee": "PeterParker"},
        {"follower": "PeterParker", "followee": "Drake"},
        {"follower": "PostMalone", "followee": "Beethoven"},
        {"follower": "Beethoven", "followee": "FreddieMercury"},
        {"follower": "Drake", "followee": "FreddieMercury"},
        {"follower": "PostMalone", "followee": "MichaelScott"},
        {"follower": "Drake", "followee": "MichaelScott"},
        {"follower": "Beethoven", "followee": "MichaelScott"},
    ]

    posts = [
        {"poster": "Drake", "song_id": 639437722},
        {"poster": "Beethoven", "original": "Drake", "song_id": 639437722},
        {"poster": "PostMalone", "original": "Drake", "song_id": 639437722},
        {"poster": "MichaelScott", "original": "Drake", "song_id": 639437722},
        {"poster": "PeterParker", "song_id": 639437722},
        {"poster": "FreddieMercury", "original": "Drake", "song_id": 639437722},
        {"poster": "Beethoven", "song_id": 5707517},
        {"poster": "Drake", "original": "Beethoven", "song_id": 5707517},
        {"poster": "PostMalone", "song_id": 3135556},
        {"poster": "PeterParker", "original": "PostMalone", "song_id": 3135556},
    ]

    for user in musers:
        add_user(user["user"], user["firstName"], user["lastName"])

    for following in followers:
        add_following(
            Profile.objects.get(user=User.objects.get(username=following["follower"])),
            Profile.objects.get(user=User.objects.get(username=following["followee"])),
        )

    for post in posts:
        add_post(post["poster"], post.get("original"), post["song_id"])


def add_user(userName, firstName, lastName):
    u, was_created = User.objects.get_or_create(
        username=userName, password=make_password("testpassword123")
    )
    u.first_name = firstName
    u.last_name = lastName
    u.save()


def add_following(follower, followee):
    f = Following.objects.create(follower=follower, followee=followee)


def add_post(posterParam, original_posterParam, song_idParam):
    po = Post.objects.create(
        poster=Profile.objects.get(user=User.objects.get(username=posterParam)),
        song_id=song_idParam,
        date=datetime.datetime.now(),
    )
    if original_posterParam:
        po.original_poster = Profile.objects.get(
            user=User.objects.get(username=original_posterParam)
        )
        po.save()


def setupAllAuth():
    current_site = Site.objects.get_current()
    current_site.socialapp_set.create(
        provider="facebook", name="facebook", client_id="0", secret="0"
    )
    current_site.socialapp_set.create(
        provider="google", name="google", client_id="0", secret="0"
    )


# The following code has been taken from
# https://docs.djangoproject.com/en/2.1/_modules/django/contrib/auth/hashers/
# It is used to hash passwords, so that the users generated by this script are valid and can be
# logged in to
@functools.lru_cache()
def get_hashers():
    hashers = []
    for hasher_path in settings.PASSWORD_HASHERS:
        hasher_cls = import_string(hasher_path)
        hasher = hasher_cls()
        if not getattr(hasher, "algorithm"):
            raise ImproperlyConfigured(
                "hasher doesn't specify an " "algorithm name: %s" % hasher_path
            )
        hashers.append(hasher)
    return hashers


# https://docs.djangoproject.com/en/2.1/_modules/django/contrib/auth/hashers/
@functools.lru_cache()
def get_hashers_by_algorithm():
    return {hasher.algorithm: hasher for hasher in get_hashers()}


# https://docs.djangoproject.com/en/2.1/_modules/django/contrib/auth/hashers/
def get_hasher(algorithm="default"):
    """
    Return an instance of a loaded password hasher.

    If algorithm is 'default', return the default hasher. Lazily import hashers
    specified in the project's settings file if needed.
    """
    if hasattr(algorithm, "algorithm"):
        return algorithm

    elif algorithm == "default":
        return get_hashers()[0]

    else:
        hashers = get_hashers_by_algorithm()
        try:
            return hashers[algorithm]
        except KeyError:
            raise ValueError(
                "Unknown password hashing algorithm '%s'. "
                "Did you specify it in the PASSWORD_HASHERS "
                "setting?" % algorithm
            )


# https://docs.djangoproject.com/en/2.1/_modules/django/contrib/auth/hashers/
def make_password(password, salt=None, hasher="default"):
    """
    Turn a plain-text password into a hash for database storage

    Same as encode() but generate a new random salt. If password is None then
    return a concatenation of UNUSABLE_PASSWORD_PREFIX and a random string,
    which disallows logins. Additional random string reduces chances of gaining
    access to staff or superuser accounts. See ticket #20079 for more info.
    """
    if password is None:
        return UNUSABLE_PASSWORD_PREFIX + get_random_string(
            UNUSABLE_PASSWORD_SUFFIX_LENGTH
        )
    hasher = get_hasher(hasher)
    salt = salt or hasher.salt()
    return hasher.encode(password, salt)


if __name__ == "__main__":
    populate()
