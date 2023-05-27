from .models import Chat
from .models import Message
from .models import Access
from users.models import User
from users.utils import get_profile
from .utils import get_chat_name
from .utils import get_chat_avatar
from .utils import get_last_message
from .utils import get_chat_messages
from .utils import get_chat_members
from .utils import get_interlocutor


def imageToUrl(image):
    if image:
        return f'http://127.0.0.1:8000{image.url}'
    return image


class ChatSerializer:
    def messageToDict(message: Message, user: User):
        author = get_profile(message.author)
        response = {
            'id': message.id,
            'author': author.name,
            'content': message.content,
            'date_create': message.date_create.strftime("%d %b %H:%M"),
            'isMyown': message.author == user,
        }

        return response

    def chatToItemDict(chat: Chat, user: User):
        last_message = get_last_message(chat)
        if last_message:
            last_message = ChatSerializer.messageToDict(last_message, user)
        else:
            return False
        
        response = {
            'id': chat.id,
            'name': get_chat_name(chat, user),
            'avatar': imageToUrl(get_chat_avatar(chat, user)),
            'lastMessage': last_message,
            'isMulty': chat.is_multy,
        }

        return response

    def chatToFullDict(chat: Chat, user: User):
        response = {
            'info': {
                'id': chat.id,
                'name': get_chat_name(chat, user),
                'avatar': imageToUrl(get_chat_avatar(chat, user)),
                'memberCount': len(get_chat_members(chat)),
                'isMulty': chat.is_multy,
            },
            'messages': [ChatSerializer.messageToDict(message, user)
                         for message in get_chat_messages(chat, user)],
        }

        if not chat.is_multy:
            response['info']['interlocutorID'] = get_interlocutor(chat, user).id

        return response

    def memberAccessToDict(member_access: Access):
        ACCESS_DESCRIPTION = {
            0: 'Banned',
            1: 'Member',
            2: 'Moderator',
            3: 'Administrator',
            4: 'Creator',
        }
        member_profile = get_profile(member_access.user)
        
        response = {
            'id': member_profile.id,
            'name': member_profile.name,
            'surname': member_profile.surname,
            'full_name': f'{member_profile.name} {member_profile.surname}',
            'avatar': imageToUrl(member_profile.avatar),
            'access': member_access.mode,
            'access_description': ACCESS_DESCRIPTION[member_access.mode],
        }

        return response
