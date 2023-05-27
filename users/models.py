from django.db import models
from django.contrib.auth.models import PermissionsMixin
from django.contrib.auth.base_user import AbstractBaseUser
from .managers import UserManager
from django.utils.translation import gettext_lazy as _

# Create your models here.


class User(AbstractBaseUser, PermissionsMixin):
    """
    The model that represents the user as a unique impersonal unit
    """
    username = models.CharField(_("username"), max_length=50, unique=True)
    email = models.EmailField(_("email"), null=True, blank=True)
    phone = models.CharField(
        _("phone number"), max_length=25, null=True, blank=True)
    date_joined = models.DateTimeField(_("date joined"), auto_now_add=True)
    is_active = models.BooleanField(_("active"), default=False)
    is_staff = models.BooleanField(_("staff"), default=False)

    is_verified = models.BooleanField(_("verifiend"), default=False)

    objects = UserManager()

    USERNAME_FIELD = "username"
    REQUIRED_FIELDS = []

    class Meta:
        verbose_name = _("user")
        verbose_name_plural = _("users")
        unique_together = ('username', 'email', 'phone')


class Profile(models.Model):
    """
    The model that represents the user as a social unit \n
    *Linked with User model by one2one 
    """
    user = models.OneToOneField(to=User, on_delete=models.CASCADE)
    name = models.CharField(max_length=50)
    surname = models.CharField(max_length=50)
    avatar = models.ImageField(upload_to="images/profile_avatars/",
                               default="images/DEFAULT_AVATAR.png",
                               blank=True)
    about = models.CharField(max_length=500)
    country = models.CharField(max_length=50, blank=True)
    city = models.CharField(max_length=50, blank=True)
    education = models.CharField(max_length=150, blank=True)
    company = models.CharField(max_length=150, blank=True)
    hobby = models.CharField(max_length=150, blank=True)

    class Meta:
        verbose_name = _('profile')
        verbose_name_plural = _('profiles')


class Friend(models.Model):
    """
    The model that determines the status of friends between two users
    """
    friends = models.ManyToManyField(User,
                                     related_name=_('friend_with'),
                                     verbose_name=_('pair of frineds'))

    class Meta:
        verbose_name = _('friendship')
        verbose_name_plural = _('friendships')


class FriendRequest(models.Model):
    """
    The model describing a friend request
    """
    inviter = models.ForeignKey(User,
                                on_delete=models.CASCADE,
                                verbose_name=_('inviter'),
                                related_name=_('invite_friends'))
    recipient = models.ForeignKey(User,
                                  on_delete=models.CASCADE,
                                  verbose_name=_('recipient'),
                                  related_name=_('invited_by'))

    message = models.CharField(verbose_name=_('inviter\'s message'),
                               max_length=150,
                               blank=True,
                               null=True)

    class Meta:
        verbose_name = _('friend request')
        verbose_name_plural = _('friend requests')
