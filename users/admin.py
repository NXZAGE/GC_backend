from django.contrib import admin
from .models import User
from .models import Profile
from .models import Friend
from .models import FriendRequest
# Register your models here.
admin.site.register(User)
admin.site.register(Profile)
admin.site.register(Friend)
admin.site.register(FriendRequest)