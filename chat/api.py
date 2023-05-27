from django.shortcuts import get_object_or_404
from django.core.exceptions import PermissionDenied
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions
from rest_framework_simplejwt.authentication import JWTAuthentication
from .models import Chat
from .models import Message
from .models import Access
from users.models import User
from .utils import chat_access
from .utils import get_chats
from .utils import get_dialog
from .utils import get_chat_members
from .utils import give_or_save_access
from .utils import ignore_or_refuse_access
from users.utils import get_user
from .serializers import ChatSerializer

class GetChat(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request, id):
        chat = get_object_or_404(Chat, id=id)
        access = chat_access(request.user.id, id)
        if access and access.mode != 0:
            pass
        else:
            raise PermissionDenied
        
        chat = ChatSerializer.chatToFullDict(chat, request.user)
        return Response({'chat': chat})
    
class GetChatInfo(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request, id):
        chat = get_object_or_404(Chat, id=id)
        access = chat_access(request.user.id, id)
        if access and access.mode != 0:
            pass
        else:
            raise PermissionDenied
        
        members = get_chat_members(chat)
        members = [ChatSerializer.memberAccessToDict(access) 
                   for access in members]
        chat = ChatSerializer.chatToItemDict(chat, request.user)
        return Response({'chat': chat, 'members': members})
    
class GetChatlist(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated]
    
    def comporator(self, chat):
        return chat['lastMessage']['date_create']
    
    def get(self, request):
        chats = get_chats(request.user)
        print(*chats)
        normilized_chats = []
        for chat in chats:
            normilized_chat = ChatSerializer.chatToItemDict(chat, request.user)
            if normilized_chat:
                normilized_chats.append(normilized_chat)
                
        normilized_chats.sort(key=self.comporator, reverse=True)
        
        return Response({'chats': normilized_chats})
    
class SendMessage(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        chat_id = request.data['chat_id']
        user = request.user
        content = request.data['content']
        chat = get_object_or_404(Chat, id=chat_id)
        access = chat_access(user.id, chat_id)
        
        if not access or access.mode == 0:
            raise PermissionDenied
        
        message = Message(chat=chat, author=user, content=content)
        message.save()
        print(message);
        message = ChatSerializer.messageToDict(message, user)
        return Response({'message': message})
        
class GetDialog(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request, id):
        if (request.user.id == id):
            raise ValueError('You can\'t talk with yourself!')
        interlocutor = get_object_or_404(User, id=id)
        dialog = get_dialog(request.user, interlocutor)

        return Response({'dialog_id': dialog.id})
    
    

class GetChatAccessMode(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request, id):
        chat = get_object_or_404(Chat, id=id)
        try: 
            access = Access.objects.get(chat=chat, user=request.user)
        except Access.DoesNotExist:
            return Response({'mode': 0})
        
        return Response({'mode': access.mode})
    
    
class EditChat(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request, id):
        chat_data = request.data
        print(dict(chat_data))
        chat = get_object_or_404(Chat, id=id)
        access = get_object_or_404(Access, user=request.user, chat=chat)
        if access.mode < 3 or not chat.is_multy:
            raise PermissionDenied
        
        chat.name = chat_data['name']
        print(chat_data)
        
        if chat_data['with_photo'] == 'true':
            if chat_data['photo_old'] == 'false':
                print('setphoto')
                chat.avatar = chat_data['photo']
        else: 
            print('setphotodefault')
            chat.avatar = 'images/DEFAULT_AVATAR.png'
        
        print(dict(chat_data)['members[]'])
        accessed_members = [get_user(id)
                            for id in dict(chat_data)['members[]']]
        current_members = [access.user
                           for access in get_chat_members(chat)]
        
        print(accessed_members)
        print(current_members)
        
        for member in current_members:
            if member not in accessed_members:
                ignore_or_refuse_access(member, chat)
            
        for member in accessed_members:
            give_or_save_access(member, chat)
            
        chat.save()
        
        return Response({'id': chat.id})
    
class CreateChat(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        chat_data = request.data
        print(chat_data)
        chat = Chat(name=chat_data['name'], is_multy=True)
        print(chat_data['with_photo']) 
        if chat_data['with_photo'] == 'true':
            chat.avatar = chat_data['photo']
        else: 
            print('setphotodefault')
            chat.avatar = 'images/DEFAULT_AVATAR.png'
            
        chat.save()
        creator_access = Access(user=request.user, chat=chat, mode=4)
        creator_access.save()
        
        first_message = Message(chat=chat, author=request.user, content="WELCOME!!!")
        first_message.save()
         
        if 'members[]' in dict(chat_data):       
            members = [get_user(int(id))
                    for id in dict(chat_data)['members[]']]
        
            for member in members:
                access = Access(chat=chat, user=member, mode=1)
                access.save()
            
        return Response({'id': chat.id})
    
class LeaveChat(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request, id):
        chat = get_object_or_404(Chat, id=id)
        access = chat_access(request.user.id, id)
        if access and access.mode != 0:
            pass
        else:
            raise PermissionDenied
        
        access.delete()
        
        return Response()