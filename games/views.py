import json

from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, logout, login
from django.urls import reverse

from .models import TalantUser
from . import talent


def index_page(request):
    if request.user.is_authenticated:
        return redirect('login')
    else:
        return render(request, 'index.html')


@login_required
def user_page(request):
    user = User.objects.get(email=request.user.email)
    return render(request, 'user_page.html', {'user': user})


def login_page(request):
    talent_oauth_client = talent.get_oauth_sess()
    redirect_uri = request.build_absolute_uri(reverse('auth'))
    uri, state = talent_oauth_client.create_authorization_url(talent.authorization_endpoint, redirect_uri=redirect_uri)
    return render(request, 'login.html', {'url': uri})


def auth_page(request):
    talent_oauth_client = talent.get_oauth_sess()
    token = talent_oauth_client.fetch_token(
        talent.token_endpoint,
        authorization_response=request.GET["code"],
        redirect_uri=request.build_absolute_uri(reverse('auth')),
    )
    user_info = talent.get_talent_info(token)
    if not User.objects.filter(email=user_info.email).exists():
        register_user(user_info, token)

    user = authenticate(request, email=user_info.email)

    if user is not None:
        login(request, user)
        return redirect('user_page')

    return redirect('index')


def register_user(talent_info: talent.TalentInfo, token):
    user = User(email=talent_info.email, first_name=talent_info.first_name, last_name=talent_info.last_name)
    user.save()
    talent_user = TalantUser(user=user, access_token=json.dumps(token))
    talent_user.save()


@login_required
def logout_page(request):
    logout(request)
    return redirect('index')
