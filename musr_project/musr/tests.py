from django.test import TestCase
from django.contrib.sites.models import Site
from django.contrib.auth.models import User
from django.urls import reverse
from django.template import Context, Template
from django.core.exceptions import SuspiciousOperation
from django.core.files.uploadedfile import SimpleUploadedFile

from .models import Profile, Post, Following

# Create your tests here.
class TravisTesterTestCase(TestCase):
    def test_unit_tests_are_understood_and_can_pass(self):
        """Unit tests run and are able to pass"""
        test_value = 5
        self.assertEqual(test_value, 5)


class ViewsTestCase(TestCase):
    def test_404_when_user_does_not_exist(self):
        resp = self.client.get("/profile/madeupuser/", follow=True)
        self.assertEqual(resp.status_code, 404)


class ProfileTestCase(TestCase):
    # TODO!
    def test_user_created_with_built_in_django_methods_has_user_profile_picture(self):
        self.user = User.objects.create_user(username="testuser", password="password")
        profile = Profile.objects.get(user=self.user)

        self.assertEqual(profile.picture.name, "profile_images/default.jpg")

    def test_user_profile_urls_ignore_case(self):
        self.user = User.objects.create_user(username="testuser", password="password")
        profile = Profile.objects.get(user=self.user)
        post = Post.objects.create(poster=profile, song_id=27)

        request = self.client.get("/profile/testuser/", follow=True)
        request1 = self.client.get("/profile/testUsER/", follow=True)
        request2 = self.client.get("/profile/TESTUSER/", follow=True)

        self.assertEqual(request.content, request1.content)
        self.assertEqual(request.content, request2.content)


class ModelTestCase(TestCase):
    def test_post_can_be_created_with_just_song_id_and_user(self):
        self.user = User.objects.create_user(username="testuser", password="password")
        profile = Profile.objects.get(user=self.user)
        post = Post.objects.create(poster=profile, song_id=27)

        self.assertTrue(isinstance(post, Post))

    def test_can_create_user(self):
        self.user = User.objects.create_user(username="testuser", password="password")

        self.assertTrue(isinstance(self.user, User))

    def test_can_create_profile(self):
        self.user = User.objects.create_user(username="testuser", password="password")
        self.profile = Profile.objects.get(user=self.user)

        self.assertTrue(isinstance(self.profile, Profile))

    def test_user_deletion_cascades(self):
        self.user = User.objects.create_user(username="testuser", password="password")
        self.user.save()

        self.profile = Profile.objects.get(user=self.user)
        self.profile.save()

        self.user.delete()

        self.assertQuerysetEqual(Profile.objects.all(), [])

    def test_can_create_following_relationship(self):
        self.follower = User.objects.create_user(
            username="testuser", password="password"
        )
        self.follower.save()

        self.follower_profile = Profile.objects.get(user=self.follower)
        self.follower_profile.save()

        self.followee = User.objects.create_user(
            username="testuser2", password="password"
        )
        self.followee.save()

        self.followee_profile = Profile.objects.get(user=self.followee)
        self.followee_profile.save()

        self.following = Following.objects.create(
            follower=self.follower_profile, followee=self.followee_profile
        )
        self.following.save()

        self.assertTrue(isinstance(self.following, Following))

    def test_user_deletion_cascades_following(self):
        self.follower = User.objects.create_user(
            username="testuser", password="password"
        )
        self.follower.save()

        self.follower_profile = Profile.objects.get(user=self.follower)
        self.follower_profile.save()

        self.followee = User.objects.create_user(
            username="testuser2", password="password"
        )
        self.followee.save()

        self.followee_profile = Profile.objects.get(user=self.followee)
        self.followee_profile.save()

        self.following = Following.objects.create(
            follower=self.follower_profile, followee=self.followee_profile
        )
        self.following.save()

        self.follower.delete()

        self.assertQuerysetEqual(Following.objects.all(), [])


# TODO: refactor these
class baseLinksTestCase(TestCase):
    @classmethod
    def setUp(self):
        self.current_site = Site.objects.get_current()
        self.SocialApp1 = self.current_site.socialapp_set.create(
            provider="facebook",
            name="facebook",
            client_id="1234567890",
            secret="0987654321",
        )
        self.SocialApp2 = self.current_site.socialapp_set.create(
            provider="google",
            name="google",
            client_id="1234567890",
            secret="0987654321",
        )

        self.user = User.objects.create_user(username="admin", password="secret")

    def test_logged_out_user_sees_sign_in_link(self):
        response = self.client.get("/", follow=True)
        self.assertIn(reverse("account_login"), response.content.decode("ascii"))
        self.assertNotIn(reverse("account_logout"), response.content.decode("ascii"))

    def test_normally_logged_in_user_sees_sign_out_link(self):
        self.client.post("/account/login/", {"login": "admin", "password": "secret"})
        response = self.client.get("/")
        self.assertNotIn(reverse("account_login"), response.content.decode("ascii"))
        self.assertIn(reverse("account_logout"), response.content.decode("ascii"))


# TODO: these could use some fleshing out
class AllAuthTestCase(TestCase):
    @classmethod
    def setUp(self):
        self.current_site = Site.objects.get_current()
        self.SocialApp1 = self.current_site.socialapp_set.create(
            provider="facebook",
            name="facebook",
            client_id="1234567890",
            secret="0987654321",
        )
        self.SocialApp2 = self.current_site.socialapp_set.create(
            provider="google",
            name="google",
            client_id="1234567890",
            secret="0987654321",
        )

        self.user = User.objects.create_user(username="admin", password="secret")

    # Most of allAuth is tested, only test our integration
    def test_login_page_uses_musr_base(self):
        response = self.client.get("/account/login/")

        self.assertContains(response, "<!-- MUSR base.html -->", status_code=200)
        self.assertTemplateUsed(response, "musr/base.html")

    def test_complain_about_empty_form(self):
        response = self.client.post(
            "/account/login/", {"login": "admin", "password": "wrongsecret"}
        )
        self.assertContains(
            response,
            "The username and/or password you specified are not correct.",
            status_code=200,
        )
        self.assertTemplateUsed(response, "account/login.html")

    def test_complain_about_wrong_password(self):
        response = self.client.post(
            "/account/login/", {"login": "admin", "password": "wrongsecret"}
        )
        self.assertContains(
            response, "The username and/or password you specified are not correct."
        )
        self.assertTemplateUsed(response, "account/login.html")

    def test_complain_about_nonexistent_user(self):
        response = self.client.post(
            "/account/login/", {"login": "fakeuser", "password": "wrongsecret"}
        )
        self.assertContains(
            response, "The username and/or password you specified are not correct."
        )
        self.assertTemplateUsed(response, "account/login.html")

    def test_redirect_to_home_after_logging_in(self):
        response = self.client.post(
            "/account/login/", {"login": "admin", "password": "secret"}
        )
        self.assertRedirects(response, "/")


class PostShowingViewTestCase(TestCase):
    @classmethod
    def setUp(self):
        self.user = User.objects.create_user(username="number_one", password="1")
        self.user.save()

        self.profile = Profile.objects.get(user=self.user)
        self.profile.save()

        self.post = Post.objects.create(
            profile=self.profile, Song_Id=1, date=datetime.datetime(2019, 2, 1, 12, 0)
        )
        self.post.save()


class AddPostTestCase(TestCase):
    @classmethod
    def setUp(self):
        self.current_site = Site.objects.get_current()
        self.SocialApp1 = self.current_site.socialapp_set.create(
            provider="facebook",
            name="facebook",
            client_id="1234567890",
            secret="0987654321",
        )
        self.SocialApp2 = self.current_site.socialapp_set.create(
            provider="google",
            name="google",
            client_id="1234567890",
            secret="0987654321",
        )

        self.user = User.objects.create_user(username="admin", password="secret")
        Profile.objects.get(user=self.user)

    def test_cant_make_post_if_not_logged_in(self):
        response = self.client.get(reverse("add_post"), follow=True)
        self.assertTemplateUsed(response, "account/login.html")

    def test_making_get_request_to_add_post_does_nothing(self):
        self.client.post("/account/login/", {"login": "admin", "password": "secret"})

        response = self.client.get(reverse("add_post"))
        self.assertRedirects(response, "/")

    def test_post_creation_sucessful(self):
        self.client.post("/account/login/", {"login": "admin", "password": "secret"})

        self.client.post(reverse("add_post"), {"song": 1}, follow=True)

        testpost = Post.objects.get(song_id=1)
        self.assertIsNotNone(testpost)


class SongTemplateTagTestCase(TestCase):
    def render_template(self, string, context=None):
        context = context or {}
        context = Context(context)
        return Template(string).render(context)

    def test_tag_handles_empty_context_dict(self):
        with self.assertRaises(SuspiciousOperation):
            self.render_template(
                "{% load musr_template_tags %}{% song post user %}", {}
            )

    def test_tag_handles_invalid_deezer_song_id(self):
        user = User.objects.create_user(username="admin", password="secret")
        profile = Profile.objects.get(user=user)
        post = Post.objects.create(post_id=1, poster=profile, song_id=27)
        with self.assertRaises(SuspiciousOperation):
            self.render_template(
                "{% load musr_template_tags %}{% song post user %}", {}
            )

    def test_tag_pulls_song_info_from_deezer(self):
        user = User.objects.create_user(username="admin", password="secret")
        image = (
            b"\x47\x49\x46\x38\x39\x61\x01\x00\x01\x00\x00\x00\x00\x21\xf9\x04"
            b"\x01\x0a\x00\x01\x00\x2c\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02"
            b"\x02\x4c\x01\x00\x3b"
        )
        profile = Profile.objects.get(user=user)
        profile.picture = SimpleUploadedFile(
            "small.gif", image, content_type="image/gif"
        )
        profile.save()
        post = Post.objects.create(post_id=1, poster=profile, song_id=3135556)
        response = self.render_template(
            "{% load musr_template_tags %}{% song post user %}", {"post": post}
        )

        self.assertInHTML("Harder Better Faster Stronger", response)
        self.assertInHTML("Discovery", response)
        self.assertInHTML("Daft Punk", response)
