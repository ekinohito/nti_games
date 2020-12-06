from dataclasses import dataclass
import json

from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.shortcuts import render, redirect
from authlib.integrations.requests_client import OAuth2Session
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, logout, login
from django.urls import reverse

from .models import TalantUser

client_id = settings.TALANT_CLIENT_ID
client_secret = settings.TALANT_CLIENT_SECRET
redirect_uri = 'http://localhost:8000/auth/'
authorization_endpoint = 'https://talent.kruzhok.org/oauth/authorize/'
token_endpoint = 'https://talent.kruzhok.org/api/oauth/issue-token/'

talant_oauth_client = OAuth2Session(client_id, client_secret, token_endpoint_auth_method='client_secret_post')


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
    uri, state = talant_oauth_client.create_authorization_url(authorization_endpoint, redirect_uri=redirect_uri)
    return render(request, 'login.html', {'url': uri})


def auth_page(request):
    token = talant_oauth_client.fetch_token(
        token_endpoint,
        authorization_response=f'{request.GET["code"]}',
        redirect_uri=redirect_uri
    )
    user_info = get_talant_info(token)
    if not User.objects.filter(email=user_info.email).exists():
        register_user(user_info, token)

    user = authenticate(request, email=user_info.email)
    print(user)
    if user is not None:
        login(request, user)
        return redirect('user_page')

    return redirect('index')


@dataclass
class TalantInfo:
    id: int
    email: str
    first_name: str
    last_name: str


def register_user(talant_info: TalantInfo, token):
    user = User(email=talant_info.email, first_name=talant_info.first_name, last_name=talant_info.last_name)
    user.save()
    talant_user = TalantUser(user=user, access_token=json.dumps(token))
    talant_user.save()


def get_talant_info(token) -> TalantInfo:
    client = OAuth2Session(client_id, client_secret, token=token)
    # id, email, first_name, last_name
    resp = client.get('https://talent.kruzhok.org/api/user/').json()
    return TalantInfo(id=resp['id'], email=resp['email'], first_name=resp['first_name'], last_name=resp['last_name'])


@login_required
def logout_page(request):
    logout(request)
    return redirect('index')
