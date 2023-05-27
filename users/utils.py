from itertools import groupby
from .models import User
from .models import Profile
from .models import Friend
from .models import FriendRequest
from .models import FriendRequest


def get_profile(user: User) -> Profile:
    profile = Profile.objects.get(user=user)
    return profile


def convert_profile_to_dict(profile: Profile):
    profile_dict = {'id': profile.id,
                    'name': profile.name,
                    'surname': profile.surname,
                    'full_name': f'{profile.name} {profile.surname}',
                    'avatar': profile.avatar}
    return profile_dict


def get_user(id: id):
    try:
        user = User.objects.get(id=id)
        return user
    except User.DoesNotExist:
        return None


def get_friends(user: User):
    def get_friend(friendship: Friend):
        friends = list(friendship.friends.all())

        if len(friends) > 2:
            raise ValueError(f'Friends is a pair of users, not {len(friends)}')

        for friend in friends:
            if friend != user:
                return friend
        raise ValueError('User cannot be friends with himself')

    friends = [get_friend(friendship)
               for friendship in user.friend_with.all()]

    return friends

def get_friend_inviters(user: User):
    invitations = FriendRequest.objects.filter(recipient=user)
    inviters = [invitation.inviter
                for invitation in invitations]
    return inviters


def are_friends(user1: User, user2: User) -> bool:
    user1_friends = get_friends(user1)
    return user2 in user1_friends


def friend_able_to_invite(inviter, recipient) -> bool:
    if inviter == recipient:
        return False

    if are_friends(inviter, recipient):
        return False

    try:
        invitation = FriendRequest.objects.get(
            inviter=inviter, recipient=recipient)
    except FriendRequest.DoesNotExist:
        pass
    else:
        return False

    try:
        invitation = FriendRequest.objects.get(
            inviter=recipient, recipient=inviter)
    except FriendRequest.DoesNotExist:
        pass
    else:
        return False

    return True


def friend_invited(inviter: User, recipient: User) -> bool:
    try:
        invitation = FriendRequest.objects.get(
            inviter=inviter, recipient=recipient)
    except FriendRequest.DoesNotExist:
        return False
    else:
        return True


def accept_friend_request(inviter: User, recipient: User):
    try:
        invitation = FriendRequest.objects.get(
            inviter=inviter, recipient=recipient)
    except FriendRequest.DoesNotExist:
        raise ValueError('Null request can\'t be accepted')
    else:
        friendship = Friend()
        friendship.save()
        friendship.friends.set([inviter, recipient])
        friendship.save()
        invitation.delete()


def get_friend_add_button_state(user_id: User, opponent_id: User):
    user = User.objects.get(id=user_id)
    opponent = User.objects.get(id=opponent_id)
    state = False
    if friend_invited(opponent, user):
        state = 'Accept friendship'
    elif friend_invited(user, opponent):
        state = 'Cancel friend request'
    elif friend_able_to_invite(user, opponent):
        state = 'Offer friendship'
    elif are_friends(user, opponent):
        state = 'Stop being friends'

    return state


def refuse_friendship(user1: User, user2: User):
    user1_friendships = Friend.objects.filter(friends__in=[user1])
    for friendship in user1_friendships:
        if user2 in friendship.friends.all():
            friendship.delete()
            return

    print('error: no friendships')


def deny_friend_request(inviter: User, recipient: User):
    invitation = FriendRequest.objects.get(
        inviter=inviter, recipient=recipient)
    invitation.delete()


def execute_find_users_querry(querry):
    response = []
    try:
        id = int(querry)
        response.extend(Profile.objects.filter(id=id))
    except ValueError:
        fullname = querry
        try:
            name, surname = list(fullname.split())
            response.extend(Profile.objects.filter(
                name=name, surname=surname))
            response.extend(Profile.objects.filter(
                name=surname, surname=name))
        except ValueError:
            name = fullname
            surname = fullname

        response.extend([profile
                         for profile
                         in Profile.objects.filter(name__icontains=name)
                         if profile not in response])
        response.extend([profile
                         for profile
                         in Profile.objects.filter(surname__icontains=surname)
                         if profile not in response])

    response = [get_user(profile.id) for profile, _ in groupby(response)]
    return response


def get_friendship_status(user: User, friend: User):
    response = {}
    response['are_friends'] = are_friends(user, friend)
    response['you_invited'] = (False if response['are_friends']
                               else friend_invited(user, friend))
    response['friend_invited'] = (False if response['are_friends']
                                  else friend_invited(friend, user))
    
    return response


def send_friend_request(user: User, friend: User):
    status = get_friendship_status(user, friend)
    if status['are_friends']:
        raise ValueError('You are already friends!')
    if status['you_invited']:
        raise ValueError('You have already sent request!')
    if status['friend_invited']:
        return accept_friend_request(user, friend)
    
    friend_request = FriendRequest(inviter=user, recipient=friend)
    friend_request.save()


def withdraw_friend_request(user: User, friend: User):
    status = get_friendship_status(user, friend)
    if status['are_friends']:
        raise ValueError('You are already friends!')
    if not status['you_invited']:
        raise ValueError('Nothing to withdraw')
    if status['friend_invited']:
        decline_friend_request(user, friend)
        
    friend_request = FriendRequest.objects.get(inviter=user, recipient=friend)
    friend_request.delete()


def accept_friend_request(user: User, friend: User):
    status = get_friendship_status(user, friend)
    if status['are_friends']:
        raise ValueError('You are already friends!')
    if not status['friend_invited']:
        raise ValueError('Nothing to accept')
    if status['you_invited']:
        raise ValueError(f'Waiting for {friend.name} accept your request')

    friend_request = FriendRequest.objects.get(inviter=friend, recipient=user)
    friendship = Friend()
    friendship.save()
    friendship.friends.add(user, friend)
    friendship.save()
    friend_request.delete()
    
    
def decline_friend_request(user: User, friend: User):
    status = get_friendship_status(user, friend)
    if status['are_friends']:
        raise ValueError('You are already friends!')
    if not status['friend_invited']:
        raise ValueError('Nothing to decline')
    if status['you_invited']:
        withdraw_friend_request()
  
    friend_request = FriendRequest.objects.get(inviter=friend, recipient=user)
    friend_request.delete()
        
