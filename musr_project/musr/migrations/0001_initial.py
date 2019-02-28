# Generated by Django 2.1.7 on 2019-02-26 21:45

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [("auth", "0009_alter_user_last_name_max_length")]

    operations = [
        migrations.CreateModel(
            name="Post",
            fields=[
                ("Post_Id", models.AutoField(primary_key=True, serialize=False)),
                ("Song_Id", models.IntegerField()),
                ("date", models.DateField()),
            ],
        ),
        migrations.CreateModel(
            name="Profile",
            fields=[
                (
                    "user",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE,
                        primary_key=True,
                        serialize=False,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                ("picture", models.ImageField(blank=True, upload_to="profile_images")),
            ],
        ),
        migrations.AddField(
            model_name="post",
            name="Original_Poster_Id",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="original_poster",
                to="musr.Profile",
            ),
        ),
        migrations.AddField(
            model_name="post",
            name="poster",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="poster",
                to="musr.Profile",
            ),
        ),
    ]