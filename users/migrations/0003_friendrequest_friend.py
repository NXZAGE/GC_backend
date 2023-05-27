# Generated by Django 4.2 on 2023-04-18 16:22

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0002_alter_profile_options'),
    ]

    operations = [
        migrations.CreateModel(
            name='FriendRequest',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('message', models.CharField(max_length=150, verbose_name="inviter's message")),
                ('inviter', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='invite_friends', to=settings.AUTH_USER_MODEL, verbose_name='inviter')),
                ('recipient', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='invited_by', to=settings.AUTH_USER_MODEL, verbose_name='recipient')),
            ],
            options={
                'verbose_name': 'friend request',
                'verbose_name_plural': 'friend requests',
            },
        ),
        migrations.CreateModel(
            name='Friend',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('friends', models.ManyToManyField(related_name='friend_with', to=settings.AUTH_USER_MODEL, verbose_name='pair of frineds')),
            ],
            options={
                'verbose_name': 'friendship',
                'verbose_name_plural': 'friendships',
            },
        ),
    ]
