from django.db import IntegrityError
from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions
from rest_framework_simplejwt.authentication import JWTAuthentication
from .serializers import UserSerializer
from .serializers import FriendSerializer
from .models import User
from .signals import user_created
from .utils import get_profile
from .utils import get_friends
from .utils import get_friend_inviters
from .utils import refuse_friendship
from .utils import execute_find_users_querry
from .utils import get_friendship_status
from .utils import send_friend_request
from .utils import withdraw_friend_request
from .utils import accept_friend_request
from .utils import decline_friend_request


class Register(APIView):
    def post(self, request, format=None):
        user_data = dict(request.data)
        response = {}

        try:
            user = User.objects.create_user(username=user_data['login'],
                                            email=user_data['email'],
                                            password=user_data['password'],
                                            is_active=True)

            user.save()

            user_created.send(sender=User,
                              user=user,
                              name=user_data['name'],
                              surname=user_data['surname'])

            response['status'] = 'success'
            response['message'] = 'User registered successfully'
            response['user'] = UserSerializer.toFullProfileDict(user)

        except IntegrityError as error:
            response['status'] = 'error'
            response['message'] = 'User with the same data is already exists'

        return Response(response)


class SelfProfile(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, format=None):
        user = UserSerializer.toFullProfileDict(request.user)
        response = {'user': user}
        return Response(response)


class GetProfile(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, id, format=None):
        user = get_object_or_404(User, id=id)
        response = {'user': UserSerializer.toFullProfileDict(user)}
        return Response(response)


class EditProfile(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        profile_data = request.data
        if not profile_data['name'] or not profile_data['surname']:
            raise ValueError('Name and surname is required!')
        
        print(profile_data)
        
        user = request.user
        profile = get_profile(user)
        profile.name = profile_data['name']
        profile.surname = profile_data['surname']
        profile.about = profile_data['about']
        profile.hobby = profile_data['hobby']
        profile.city = profile_data['city']
        profile.education = profile_data['education']
        profile.company = profile_data['company']
        
        if profile_data['with_photo'] == 'true':
            if profile_data['photo_old'] == 'false':
                print('setphoto')
                profile.avatar = profile_data['photo']
        else: 
            print('setphotodefault')
            profile.avatar = 'images/DEFAULT_AVATAR.png'
        
        profile.save()
        
        return Response({'id': profile.id})

class GetFriendList(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, id):
        user = get_object_or_404(User, id=id)
        user_friends = get_friends(user)
        user_friends = [FriendSerializer.toDict(friend)
                        for friend in user_friends]

        return Response({'friends': user_friends})
    
class GetFriendRequestList(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        inviters = get_friend_inviters(request.user)
        inviters = [FriendSerializer.toDict(inviter)
                    for inviter in inviters]
        
        return Response({'inviters': inviters})


class RefuseFriendship(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def refuse_request_permission(self, user_id, user1_id, user2_id):
        return user_id == user1_id or user_id == user2_id

    def post(self, request):
        user1 = get_object_or_404(User, id=request.data['user1_id'])
        user2 = get_object_or_404(User, id=request.data['user2_id'])
        if not self.refuse_request_permission(request.user.id,
                                              user1.id,
                                              user2.id):
            raise PermissionError('It\'s not your friendship!!!')

        refuse_friendship(user1, user2)
        
        return Response()


class FindUser(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        querry = request.data['querry']
        users = execute_find_users_querry(querry)
        users = [UserSerializer.toShortProfileDict(user)
                 for user in users]
        return Response({'users': users})


class GetFriendshipStatus(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, friend_id):
        friend = get_object_or_404(User, id=friend_id)
        status = get_friendship_status(request.user, friend)

        return Response({'status': status})


class SendFriendRequest(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, friend_id):
        friend = get_object_or_404(User, id=friend_id)
        if friend.id == request.user.id:
            raise ValueError('Denied: sending request to yourself')
        send_friend_request(request.user, friend)
        
        return Response({'status': 'ok'})


class WithdrawFriendRequest(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, friend_id):
        friend = get_object_or_404(User, id=friend_id)
        if friend.id == request.user.id:
            raise ValueError('Denied: withdrawing request to yourself')
        withdraw_friend_request(request.user, friend)
        
        return Response({'status': 'ok'})
        

class AcceptFriendRequest(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, friend_id):
        friend = get_object_or_404(User, id=friend_id)
        if friend.id == request.user.id:
            raise ValueError('Denied: accept request for yourself')
        accept_friend_request(request.user, friend)
        
        return Response({'status': 'ok'})


class DeclineFriendRequest(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, friend_id):
        friend = get_object_or_404(User, id=friend_id)
        if friend.id == request.user.id:
            raise ValueError('Denied: decline request for yourself')
        decline_friend_request(request.user, friend)
        
        return Response({'status': 'ok'})