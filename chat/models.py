from django.db import models
from django.utils.translation import gettext_lazy as _
from users.models import User

# Create your models here.


class Chat(models.Model):
    """
    Base model of chat
    """
    name = models.CharField(max_length=50, blank=True,
                            verbose_name=_('chat name'))
    avatar = models.ImageField(upload_to="images/chat_avatars/",
                               default="images/DEFAULT_CHAT_AVATAR.jpg",
                               blank=True)
    is_multy = models.BooleanField(default=False,
                                   verbose_name=_('is multichat'))
    date_create = models.DateTimeField(auto_now=True,
                                       verbose_name=_('date of creation'))

    class Meta:
        verbose_name = _('chat')
        verbose_name_plural = _('chats')


class Message(models.Model):
    """
    Base model of message
    """
    chat = models.ForeignKey(to=Chat, on_delete=models.CASCADE,
                             verbose_name=_('chat'))
    author = models.ForeignKey(to=User, on_delete=models.CASCADE,
                               verbose_name=_('author'))
    content = models.TextField(verbose_name=_('content'))
    is_read = models.BooleanField(default=False, 
                                  verbose_name=_('message has been read'))
    date_create = models.DateTimeField(auto_now=True,
                                       verbose_name=_('date of creation'))

    class Meta:
        verbose_name = _('message')
        verbose_name_plural = _('messages')


class Access(models.Model):
    """
    Model for access user to chat
    \n
    Access modes:
    0: No access
    1: Member
    2: Moderator
    3: Admin
    4: Creator
    """
    user = models.ForeignKey(to=User, on_delete=models.CASCADE,
                             verbose_name=_('user'))
    chat = models.ForeignKey(to=Chat, on_delete=models.CASCADE,
                             verbose_name=_('chat'))
    mode = models.IntegerField(default=1, verbose_name=_('access mode'))

    class Meta:
        verbose_name = _('access')
        verbose_name_plural = _('accesses')
