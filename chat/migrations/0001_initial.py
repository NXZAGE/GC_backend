# Generated by Django 4.2.1 on 2023-05-27 08:11

from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Access",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("mode", models.IntegerField(default=1, verbose_name="access mode")),
            ],
            options={
                "verbose_name": "access",
                "verbose_name_plural": "accesses",
            },
        ),
        migrations.CreateModel(
            name="Chat",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "name",
                    models.CharField(
                        blank=True, max_length=50, verbose_name="chat name"
                    ),
                ),
                (
                    "avatar",
                    models.ImageField(
                        blank=True,
                        default="images/DEFAULT_CHAT_AVATAR.jpg",
                        upload_to="images/chat_avatars/",
                    ),
                ),
                (
                    "is_multy",
                    models.BooleanField(default=False, verbose_name="is multichat"),
                ),
                (
                    "date_create",
                    models.DateTimeField(
                        auto_now=True, verbose_name="date of creation"
                    ),
                ),
            ],
            options={
                "verbose_name": "chat",
                "verbose_name_plural": "chats",
            },
        ),
        migrations.CreateModel(
            name="Message",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("content", models.TextField(verbose_name="content")),
                (
                    "is_read",
                    models.BooleanField(
                        default=False, verbose_name="message has been read"
                    ),
                ),
                (
                    "date_create",
                    models.DateTimeField(
                        auto_now=True, verbose_name="date of creation"
                    ),
                ),
            ],
            options={
                "verbose_name": "message",
                "verbose_name_plural": "messages",
            },
        ),
    ]
