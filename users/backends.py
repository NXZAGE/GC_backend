from .models import User
from django.db.models import Q
#from django.contrib.auth.backends import ModelBackend

class AuthBackend(object):
    """
    Custom authetication backend which allows to login with
    username/email/phone and password
    """
    supports_object_permission = True
    supports_anonymous_user = False
    supports_inactive_user = False
    
    def get_user(self, name):
        try:
            return User.objects.get(username=name)
        except User.DoesNotExist:
            return None
        
    def authenticate(self, request, username, password):
        try:
            user = User.objects.get(
                Q(username=username) | Q(email=username) | Q(phone=username)
            )
        except User.DoesNotExist:
            return None
        if user.check_password(password):
            return user
        else:
            return None
