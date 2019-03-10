# Generated by Django 2.1.7 on 2019-03-05 11:58

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [("musr", "0003_auto_20190302_1244")]

    operations = [
        migrations.AlterModelOptions(
            name="post", options={"ordering": ("-date", "-post_id")}
        ),
        migrations.AlterField(
            model_name="post",
            name="date",
            field=models.DateField(default=django.utils.timezone.now),
        ),
    ]
