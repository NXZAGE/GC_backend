from django.db import models
from django.utils.translation import gettext_lazy as _
from users.models import User
# Create your models here.


class Post(models.Model):
    """
    Model for user posts
    """
    author = models.ForeignKey(to=User, 
                               on_delete=models.CASCADE, 
                               verbose_name=_('author'))
    content = models.TextField(verbose_name=_('text content'))
    photo = models.ImageField(upload_to='images/post_attachments/',
                              blank=True,
                              null=True,
                              verbose_name=_('photo attachment'))
    date_create = models.DateTimeField(auto_now=True, 
                                       verbose_name='date of creation')
    is_edited = models.BooleanField(default=False, 
                                    verbose_name=_('is edited'))
    
    class Meta:
        verbose_name = _('post')
        verbose_name_plural = _('posts')


class Comment(models.Model):
    """
    Model for user comments for posts
    """
    post = models.ForeignKey(to=Post, 
                             on_delete=models.CASCADE,
                             verbose_name=_('commented post'))
    author = models.ForeignKey(to=User, 
                               on_delete=models.CASCADE,
                               verbose_name=_('author'))
    content = models.TextField(verbose_name=_('text content'))
    date_create = models.DateTimeField(auto_now=True,
                                       verbose_name=_('date of creation'))
    is_edited = models.BooleanField(default=False,
                                    verbose_name=_('is edited'))
    
    class Meta:
        verbose_name = _('comment')
        verbose_name_plural = _('comments')


class Bookmark(models.Model):
    post = models.ForeignKey(to=Post, on_delete=models.CASCADE)
    user = models.ForeignKey(to=User, on_delete=models.CASCADE)
    date = models.DateTimeField(auto_now=True)
