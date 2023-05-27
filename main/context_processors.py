from users.models import Profile


def get_self_profile(request):
    """
    Context processor which returns context with information
    about the profile of the authenticated user
    """
    if request.user.is_authenticated:
        profile = Profile.objects.get(user=request.user)
    else:
        context = {'self_profile': {'id': -1,
                               'name': 'Anonymous',
                               'surname': 'Anonymous',
                               'full_name': 'Anonymous Anonymous',
                               'avatar': 'images/ANONYMOUS_AVATAR.png',
                               }}
        return context

    context = {'self_profile': {'id': profile.id,
                           'name': profile.name,
                           'surname': profile.surname,
                           'full_name': f'{profile.name} {profile.surname}',
                           'avatar': profile.avatar,
                           }}

    return context
