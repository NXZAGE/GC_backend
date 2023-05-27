from .models import Post
from .models import Comment
from users.models import User
from .utils import is_in_bookmark
from users.serializers import UserSerializer 

BASE_MEDIA_URL = 'http://127.0.0.1:8000'
class PostSerializer:
    def toDict(post: Post, user: User):
        response = {
            'id': post.id,
            'author': UserSerializer.toShortProfileDict(post.author),
            'content': post.content,
            'photo': BASE_MEDIA_URL + post.photo.url if post.photo else False,
            'isBookmark': is_in_bookmark(user, post),
        }
        
        return response
    
class CommentSerializer:
    def toDict(comment: Comment):
        response = {
            'author': UserSerializer.toShortProfileDict(comment.author),
            'content': comment.content,
            'timestamp': comment.date_create.strftime("%d %b %H:%M"),
        }
        
        return response