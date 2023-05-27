from django.shortcuts import render
from django.shortcuts import redirect
from django.shortcuts import get_object_or_404
from django.contrib.auth import login
from django.contrib.auth import authenticate
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.urls import reverse
from .forms import LoginForm
from .forms import RegistrationForm
from .forms import ProfileEditForm
from .models import User
from .models import Friend
from .models import Profile
from .models import FriendRequest
from .utils import get_profile
from .utils import get_friends
from .utils import convert_profile_to_dict
from .utils import friend_able_to_invite
from .utils import accept_friend_request
from .utils import are_friends
from .utils import refuse_friendship
from .utils import friend_invited
from .utils import deny_friend_request
from .signals import user_created
from users.utils import get_friend_add_button_state
    
def registration_page(request):
    """
    View function which processes the user registration form 
    and performs the registration of new user.
    """
    if request.user.is_authenticated:
        return redirect('self-profile')

    context = {}

    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            context['form'] = form

            u_name = form.data['name']
            u_surname = form.data['surname']
            u_login = form.data['login']
            u_email = form.data['email']
            u_password = form.data['password']

            try:
                user = User.objects.create_user(username=u_login,
                                                email=u_email,
                                                password=u_password,
                                                is_active=True)

                user.save()

                user_created.send(sender=User,
                                  user=user,
                                  name=u_name,
                                  surname=u_surname)

                user = authenticate(request, username=u_login, password=u_password)
                login(request, user)
                
                return redirect('self-profile')
            except IntegrityError as error:
                context['form'] = form
                is_login_unique = False
                is_email_unique = False

                try:
                    User.objects.get(username=u_login)
                except User.DoesNotExist:
                    is_login_unique = True

                try:
                    User.objects.get(email=u_email)
                except User.DoesNotExist:
                    is_email_unique = True

                if not is_login_unique and not is_email_unique:
                    not_unique_fields = 'login, email'
                elif not is_login_unique:
                    not_unique_fields = 'login'
                elif not is_email_unique:
                    not_unique_fields = 'email'

                message = f"""
                Пользователь с таким именем уже существует
                Посмотрите это поле: {not_unique_fields}.
                """

                context['message'] = message

                print(error)

        else:
            context['form'] = form

    else:
        context['form'] = RegistrationForm()

    return render(request, 'registration.html', context=context)


def login_page(request):
    """
    View function which processes the user authorization form 
    and performs the authorization.
    """
    if request.user.is_authenticated:
        return redirect('self-profile')

    context = {}

    if request.method == 'POST':
        auth_form = LoginForm(request.POST)

        if auth_form.is_valid():
            username = auth_form.data['username']
            password = auth_form.data['password']
            user = authenticate(request, username=username, password=password)

            if user is not None:
                login(request, user)
                return redirect('self-profile')

            context['message'] = """
            Неправильный логин или пароль
            """
            context['form'] = auth_form

        else:
            context['form'] = LoginForm()

    else:
        context['form'] = LoginForm()

    return render(request, 'login.html', context=context)

@login_required
def settings_profile(request):
    context = {}

    if request.method == 'POST':
        form = ProfileEditForm(request.POST)
        if form.is_valid():
            context['form'] = form
            profile = get_profile(request.user)
            profile.name = form.cleaned_data['name']
            profile.surname = form.cleaned_data['surname']
            profile.about = form.cleaned_data['about']
            profile.country = form.cleaned_data['country']
            profile.city = form.cleaned_data['city']
            profile.education = form.cleaned_data['education']
            profile.company = form.cleaned_data['company']
            profile.hobby = form.cleaned_data['hobby']
            print(dict(request.FILES))
            if 'avatar-profile-form' in dict(request.FILES):
                photo = dict(request.FILES)['avatar-profile-form']
                profile.avatar = photo[0]
            elif dict(request.POST)['is_del'][0] == "1":
                profile.avatar = "images/DEFAULT_AVATAR.png"
            profile.save()
            return redirect('self-profile')
        else:
            context['form'] = form

    else:
        profile = get_profile(request.user)
        form_init = {'name': profile.name,
                     'surname': profile.surname,
                     'about': profile.about,
                     'country': profile.country,
                     'city': profile.city,
                     'education': profile.education,
                     'company': profile.company,
                     'hobby': profile.hobby}
        context['form'] = ProfileEditForm(initial=form_init)
        context['avatar_name'] = profile.avatar.name.split('/')[-1]
        context['avatar_url'] = profile.avatar.url
        context['avatar_value'] = profile.avatar
    return render(request, 'settings_profile.html', context=context)

@login_required
def friend_list(request, id):
    try:    
        current_user = User.objects.get(id=id)
    except User.DoesNotExist:
        return redirect('home')
    profile = Profile.objects.get(id=id)
    context = {'profile': {'id': profile.id,
                           'name': profile.name
                           }
               }
    
    friends = get_friends(current_user)
    friends = [convert_profile_to_dict(get_profile(friend))
               for friend in friends]
    if current_user == request.user:
        friend_requests = FriendRequest.objects.filter(recipient=request.user)
        inviters = [get_profile(friend_request.inviter)
                    for friend_request in friend_requests]
        context['friend_inviters'] = [convert_profile_to_dict(inviter)
                                      for inviter in inviters]
        context['add_friend_button'] = get_friend_add_button_state(request.user.id, id)
    context['friends'] = friends
    return render(request, 'friendlist.html', context)




@login_required
def invite_friend(request, recipient_id):
    try:
        recipient = User.objects.get(id=recipient_id)
    except User.DoesNotExist:
        print('UNKNOWN PERSON')
        return redirect('self-profile')
    
    inviter = request.user
    
    if friend_able_to_invite(inviter, recipient):
        invitation = FriendRequest(inviter=inviter, recipient=recipient)
        invitation.save()
        print('REQUEST SENDED')
        return redirect(reverse('friend-list', args=[request.user.id]))
    elif are_friends(inviter, recipient):
        refuse_friendship(inviter, recipient)
        return redirect(reverse('friend-list', args=[request.user.id]))
    elif friend_invited(inviter, recipient):
        deny_friend_request(inviter, recipient)
        return redirect(reverse('friend-list', args=[request.user.id]))
    else:
        try:
            accept_friend_request(recipient, inviter)
        except ValueError:
            print('REQUEST DENIED')
            return redirect(reverse('friend-list', args=[request.user.id]))
        else:
            return redirect(reverse('friend-list', args=[request.user.id]))


@login_required
def reject_request_friend(request, recipient_id):
    try:
        recipient = User.objects.get(id=recipient_id)
    except User.DoesNotExist:
        print('UNKNOWN PERSON')
        return redirect('self-profile')

    inviter = request.user

    if friend_able_to_invite(inviter, recipient):
        invitation = FriendRequest(inviter=inviter, recipient=recipient)
        invitation.save()
        print('REQUEST SENDED')
        return redirect(reverse('friend-list', args=[request.user.id]))
    elif are_friends(inviter, recipient):
        refuse_friendship(inviter, recipient)
        return redirect(reverse('friend-list', args=[request.user.id]))
    elif friend_invited(inviter, recipient):
        deny_friend_request(inviter, recipient)
        return redirect(reverse('friend-list', args=[request.user.id]))
    else:
        try:
            deny_friend_request(recipient, inviter)
        except ValueError:
            print('REQUEST DENIED')
            return redirect(reverse('friend-list', args=[request.user.id]))
        else:
            return redirect(reverse('friend-list', args=[request.user.id]))

@login_required
def logout_page(request):
    logout(request)
    return redirect('home')