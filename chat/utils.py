from __future__ import annotations

from .models import Message
from .models import Chat
from .models import Access
from django.db.models.fields.files import ImageFieldFile
from django.urls import reverse
from users.models import User
from main.models import Bookmark
from users.utils import get_profile
from users.utils import convert_profile_to_dict

def get_chats(user) -> list:
    chats = [access.chat
             for access
             in Access.objects.filter(user=user)
             if access.mode > 0]

    return chats


def generate_chat(chat: Chat, current_user: User) -> dict:
    response = {'id': chat.id,
                'name': get_chat_name(chat, current_user),
                'avatar': get_chat_avatar(chat, current_user),
                'last_message': get_last_message(chat),
                'is_multy': chat.is_multy,
                'info_link': get_chat_info_link(chat, current_user)}

    return response


def get_last_message(chat: Chat) -> Message:
    message = Message.objects.filter(chat=chat).last()
    return message

def get_interlocutor(chat: Chat, current_user: User) -> User | None:
    if chat.is_multy:
        return None
    
    members = [access.user
               for access
               in Access.objects.filter(chat=chat)]

    for member in members:
        if member == current_user:
            continue
        interlocutor = member
        
    return interlocutor

def get_chat_name(chat: Chat, current_user: User) -> str:
    if chat.is_multy:
        return chat.name

    friend = get_interlocutor(chat, current_user)
    friend = get_profile(friend)

    return f'{friend.name} {friend.surname}'


def get_chat_avatar(chat: Chat, current_user: User) -> ImageFieldFile:
    if chat.is_multy:
        return chat.avatar

    friend = get_interlocutor(chat, current_user)
    friend = get_profile(friend)

    return friend.avatar

def get_chat_info_link(chat: Chat, current_user: User):
    if chat.is_multy:
        return reverse('multychat-info', args=[chat.id])
    else:
        return reverse('profile', args=[get_interlocutor(chat, current_user).id])

def get_chat_messages(chat: Chat, current_user: User):
    messages = Message.objects.filter(chat=chat)

    return messages


def send_message(chat, author, content):
    message = Message(chat=chat,
                      author=author,
                      content=content,
                      is_read=False)
    message.save()


def create_dialog(user1: User, user2: User) -> Chat:
    dialog = Chat(is_multy=False)
    dialog.save()
    access1 = Access(chat=dialog, user=user1, mode=4)
    access2 = Access(chat=dialog, user=user2, mode=4)
    access1.save()
    access2.save()
    return dialog


def dialog_created(user1: User, user2: User) -> Chat | None:
    user1_chats = get_chats(user1)
    for chat in user1_chats:
        if not chat.is_multy:
            try:
                user2_access = Access.objects.get(user=user2, chat=chat)
                return chat
            except Access.DoesNotExist:
                continue

    return None


def get_dialog(user1, user2) -> None:
    dialog = dialog_created(user1, user2)
    if dialog is not None:
        return dialog
    else:
        return create_dialog(user1, user2)


def chat_access(user_id, chat_id) -> bool | Access:
    try:
        user = User.objects.get(id=user_id)
        chat = Chat.objects.get(id=chat_id)
    except User.DoesNotExist or Chat.DoesNotExist:
        return False

    try:
        access = Access.objects.get(user=user, chat=chat)
    except Access.DoesNotExist:
        return False

    return access

def normalize_chat_member(member_access: Access) -> dict:
    ACCESS_DESCRIPTION = {
        0: 'Banned',
        1: 'Member',
        2: 'Moderator',
        3: 'Administrator',
        4: 'Creator',
    }
    
    member_profile = get_profile(member_access.user)
    normalized_member = {
        'id': member_profile.id,
        'name': member_profile.name,
        'surname': member_profile.surname,
        'full_name': f'{member_profile.name} {member_profile.surname}',
        'avatar': member_profile.avatar,
        'access': member_access.mode,
        'access_description': ACCESS_DESCRIPTION[member_access.mode],
    }
    
    return normalized_member

def get_chat_members(chat: Chat) -> list:
    members = Access.objects.filter(chat=chat)
    members = [access
               for access in members
               if access.mode > 0]
    return members

def give_or_save_access(user: User, chat: Chat) -> None:
    try:
        access = Access.objects.get(user=user, chat=chat)
    except Access.DoesNotExist:
        access = Access(user=user, chat=chat, mode=1)
        access.save()
    else:
        if access.mode == 0:
            access.mode = 1
            access.save()
            
def ignore_or_refuse_access(user: User, chat: Chat) -> None:
    try:
        access = Access.objects.get(user=user, chat=chat)
    except Access.DoesNotExist:
        pass
    else:
        if access.mode != 0:
            access.mode = 0
            access.save()
            
def leave_chat(user: User, chat: Chat) -> None:
    access = Access.objects.get(user=user, chat=chat)
    access.delete()
