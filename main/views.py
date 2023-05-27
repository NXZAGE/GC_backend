from django.shortcuts import render
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.urls import reverse
from users.models import Profile
from users.models import User
from users.utils import get_friend_add_button_state, get_profile
from main.models import Post, Bookmark
from main.models import Comment
from .forms import PostForm, EditPostForm
from .forms import CommentForm
from .utils import get_bookmarks, is_in_bookmark
from .forms import FrindSearchRequestForm
from itertools import groupby


@login_required
def self_profile(request):
    return redirect(f'/profile/{request.user.id}')


def main_page(request):
    posts = Post.objects.all()
    if request.user.id != None:
        context = {'posts': [{'id': post.id,
                              'author': get_profile(post.author),
                              'author_photo': get_profile(post.author).avatar,
                              'photo': post.photo,
                              'content': post.content,
                              'date': post.date_create,
                              'in_bookmarks': is_in_bookmark(request.user, post)
                              } for post in reversed(posts)]
                   }
    else:
        context = {'posts': [{'id': post.id,
                              'author': get_profile(post.author),
                              'author_photo': get_profile(post.author).avatar,
                              'photo': post.photo,
                              'content': post.content,
                              'date': post.date_create,
                              'in_bookmarks': 0
                              } for post in reversed(posts)]
                   }
    return render(request, 'main_page.html', context)


@login_required
def add_post_page(request):
    context = {}

    if request.method == 'POST':
        post_form = PostForm(request.POST, request.FILES)
        if post_form.is_valid():
            post_author = request.user
            post_content = post_form.cleaned_data.get('content')
            post_photo = post_form.cleaned_data.get('photo')
            post = Post(author=post_author, content=post_content, photo=post_photo)
            post.save()
            return redirect('self-profile')

        context['form'] = post_form
        context['message'] = 'Incorrect form, try again'
    else:
        context['form'] = PostForm()

    return render(request, 'add_post_page.html', context)

@login_required
def edit_post(request, id: int):
    context = {}
    post = Post.objects.get(id=id)
    if request.method == 'POST':
        post_form = EditPostForm(request.POST, request.FILES)
        if post_form.is_valid():
            post_author = request.user
            post_content = post_form.cleaned_data.get('content')
            post_photo = post_form.cleaned_data.get('photo')
            post.author = post_author
            post.content = post_content
            is_del = post_form.cleaned_data.get('is_del')
            if post_photo or is_del == "1":
                post.photo = post_photo
            post.save()
            return redirect('self-profile')

        context['form'] = post_form
        context['message'] = 'Incorrect form, try again'
    else:
        form_init = {
                    'content': post.content,
                    'photo': post.photo,
                     }
        if post.photo:
            context = {
                'post': {
                    'content': post.content,
                    'photo': post.photo,
                    'photo_name': post.photo.name.split('/')[-1]
                }
            }
            request.FILES['photo'] = post.photo
        else:
            context = {
                'post': {
                    'content': post.content,
                }
            }
        context['form'] = EditPostForm(form_init)
    return render(request, 'edit_post_page.html', context)



@login_required
def find_friend_page(request):
    context = {}
    
    if request.method == 'POST':
        form = FrindSearchRequestForm(request.POST)
        if form.is_valid():
            response = []
            querry = form.data['querry']
            try:
                id = int(querry)
                response.extend(Profile.objects.filter(id=id))
            except ValueError:
                fullname = querry
                
                try:
                    name, surname = list(fullname.split())
                    response.extend(Profile.objects.filter(name=name, surname=surname))
                    response.extend(Profile.objects.filter(name=surname, surname=name))
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
                
            context['form'] = form                
            context['response'] = [profile for profile, _ in groupby(response)]
        else:
            context['form'] = form
            context['message'] = 'Incorrect request!'
    else:
        context['form'] = FrindSearchRequestForm()

    return render(request, 'find_friend_page.html', context)


@login_required
def bookmarks_page(request):
    posts = get_bookmarks(request.user)
    context = {}
    if posts:
        context = {
            'posts': [{'id': post.id,
                       'author': get_profile(post.author),
                       'author_photo': get_profile(post.author).avatar,
                       'content': post.content,
                       'photo': post.photo,
                       'in_bookmarks': is_in_bookmark(request.user, post)
                       } for post in reversed(posts)]
        }
    return render(request, 'bookmarks_page.html', context)

@login_required
def add_or_delete_bookmark(request, post_id):
    try:
        post = Post.objects.get(id=post_id)
    except Post.DoesNotExist:
        return redirect('home')
    
    try:
        bookmark = Bookmark.objects.get(post=post, user=request.user)
        bookmark.delete()
    except Bookmark.DoesNotExist:
        bookmark = Bookmark(post=post, user=request.user)
        bookmark.save()

    return redirect('bookmarks')

# Заглушка для проверки чужого профиля

@login_required
def settings_page(request):
    return render(request, 'settings.html')


@login_required
def chat_page(request):
    return render(request, 'chat_list.html')


@login_required
def messenger_page(request):
    return render(request, 'messenger.html')


@login_required
def settings_profile_page(request, id: int):
    profile = Profile.objects.get(id=id)

    context = {'profile': {'id': profile.id,
                           'name': profile.name,
                           'surname': profile.surname,
                           'avatar': profile.avatar,
                           'about': profile.about,
                           'country': profile.country,
                           'city': profile.city,
                           'education': profile.education,
                           'company': profile.company,
                           'hobby': profile.hobby,
                           }
               }

    return render(request, 'settings_profile.html', context=context)

    # Заглушка !!!!! !!! !! ! ! ! ! ! !  !


def profile(request, id: int):
    """
    View function which represents page with wall of the current user by id
    """
    try:
        user = User.objects.get(id=id)
    except:
        return redirect('home')
    
    profile = Profile.objects.get(user=user)
    posts = Post.objects.filter(author=user)

    context = {'profile': {'id': profile.id,
                           'name': profile.name,
                           'surname': profile.surname,
                           'avatar': profile.avatar,
                           'about': profile.about,
                           'country': profile.country,
                           'city': profile.city,
                           'education': profile.education,
                           'company': profile.company,
                           'hobby': profile.hobby,
                           },
               'posts': [{'id': post.id,
                          'author': {'name': get_profile(post.author).name + ' ' + get_profile(post.author).surname,
                                     'link': f'/profile/{post.author.id}',
                                     },
                          'author_photo': get_profile(post.author).avatar,
                          'photo': post.photo,
                          'content': post.content,
                          'date': post.date_create,
                          'in_bookmarks': is_in_bookmark(request.user, post)
                          } for post in reversed(posts)],
               'add_friend_button': get_friend_add_button_state(request.user.id, id)
               }

    return render(request, 'profile.html',  context=context)


def post(request, id: int):
    """
    View function which represents the page with current post by id 
    and comments for that post
    """
    try:
        post = Post.objects.get(id=id)
        comments = Comment.objects.filter(post=post)
    except Post.DoesNotExist:
        return redirect('home')
    
    context = {}
    
    if request.method == 'POST':
        comment_form = CommentForm(request.POST)
        if comment_form.is_valid():
            comment_author = request.user
            comment_content = comment_form.data['content']
            comment = Comment(author=comment_author, post=post, content=comment_content)
            comment.save()
            context['form'] = CommentForm()
        else:
            context['form'] = comment_form
            context['message'] = 'Incorrect form, try again'
    else:
        context['form'] = CommentForm()
        
    context = {'post': {'id': post.id,
                        'author': {'name': get_profile(post.author).name + ' ' + get_profile(post.author).surname,
                                   'id':post.author.id,
                                   'link': f'/profile/{post.author.id}',
                                   },
                        'content': post.content,
                        'photo': post.photo,
                        'date': post.date_create,
                        },
               'comments': [{'author': get_profile(comment.author),
                             'content': comment.content,
                             'date': comment.date_create
                             } for comment in reversed(comments)],
               'form': context['form']
               }

    return render(request, 'post_template.html', context=context)

def post_delete(request, id: int):
    post = Post.objects.get(id=id)
    post.delete()
    return redirect('self-profile')