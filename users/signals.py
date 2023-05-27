from django.dispatch import receiver
from django.dispatch import Signal
from django.db import IntegrityError
from .models import User
from .models import Profile

user_created = Signal()

@receiver(user_created, sender=User)
def create_profile(user, name, surname, **kwargs):
    print('signal catched')
    try:
        profile = Profile.objects.create(
            user=user,
            name=name,
            surname=surname,
        )
        
        profile.save()
    except IntegrityError as error:
        print(error)