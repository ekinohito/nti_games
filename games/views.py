import json
from urllib.parse import urlencode

from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, logout, login
from django.urls import reverse
from django.conf import settings
import requests
import time
from celery import current_app

from .models import TalantUser
from . import talent
from . import tasks


def index_page(request):
    return render(request, 'index.html')


@login_required
def user_page(request):
    return render(request, 'user_page.html', {'user': request.user})


def login_page(request):
    # TODO: Разобраться с ссылкой и https

    redirect_uri = request.build_absolute_uri(reverse('auth'))
    uri, state = talent.get_oauth_sess().create_authorization_url(
        talent.authorization_endpoint, response_type='code',
        nonce=time.time(), redirect_uri=redirect_uri
    )
    return render(request, 'login.html', {'url': uri})


def auth_page(request):
    # TODO: Add support of denying
    #  GET '/auth/?error=access_denied&error_description=The+resource+owner+or+authorization+server+denied+the+request'

    token = requests.post(talent.token_endpoint, data={
        'grant_type': 'authorization_code',
        'scope': 'openid',
        'nonce': time.time(),
        'client_id': talent.client_id,
        'client_secret': talent.client_secret,
        'redirect_uri': request.build_absolute_uri(reverse('auth')),
        'code': request.GET['code'],
    }).json()

    # token = talent.get_oauth_sess().fetch_access_token(
    #     talent.token_endpoint,
    #     grant_type='authorization_code',
    #     scope='openid',
    #     nonce=time.time(),
    #     redirect_uri=request.build_absolute_uri(reverse('auth')),
    #     code=request.GET['code'],
    # )

    user_info = talent.get_talent_info(token)
    if not User.objects.filter(email=user_info.email).exists():
        register_user(user_info, token)

    user = authenticate(request, email=user_info.email)

    if user is not None:
        login(request, user)
        return redirect('user_page')

    return redirect('index')


def register_user(talent_info: talent.TalentInfo, token):
    user = User(email=talent_info.email, username=talent_info.email, first_name=talent_info.first_name,
                last_name=talent_info.last_name)
    user.save()
    talent_user = TalantUser(user=user, access_token=json.dumps(token))
    talent_user.save()


@login_required
def steam_login(request):
    redirect_uri = request.build_absolute_uri(reverse('steam_auth'))
    params = {
        'openid.ns': settings.OPEN_ID_NS,
        'openid.identity': settings.OPEN_ID_IDENTITY,
        'openid.claimed_id': settings.OPEN_ID_CLAIMED_ID,
        'openid.mode': 'checkid_setup',
        'openid.return_to': redirect_uri,
        'openid.realm': request.build_absolute_uri(reverse('index')),
    }

    auth_url = settings.FORMAT_STEAM_AUTH_URL.format(urlencode(params))
    return redirect(auth_url)


@login_required
def steam_auth(request):
    request.user.talantuser.steam_openid = request.GET['openid.identity']
    request.user.talantuser.steam_id = int(request.GET['openid.identity'].split('/')[-1])
    request.user.talantuser.save()
    # <QueryDict: {
    #   'openid.ns': ['http://specs.openid.net/auth/2.0'],
    #   'openid.mode': ['id_res'],
    #   'openid.op_endpoint': ['https://steamcommunity.com/openid/login'],
    #   'openid.claimed_id': ['https://steamcommunity.com/openid/id/76561198247304156'],
    #   'openid.identity': ['https://steamcommunity.com/openid/id/76561198247304156'],
    #   'openid.return_to': ['http://localhost:8000/steam/auth'],
    #   'openid.response_nonce': ['2020-12-07T14:30:09ZTQ2iswQERox0QdJj3z7TaJyaSHk='],
    #   'openid.assoc_handle': ['1234567890'],
    #   'openid.signed': ['signed,op_endpoint,claimed_id,identity,return_to,response_nonce,assoc_handle'],
    #   'openid.sig': ['TWCPNyTh59oRkjUr2ei392alTfM=']}>
    return redirect('user_page')


@login_required
def steam_logout(request):
    request.user.talantuser.steam_openid = ''
    request.user.talantuser.steam_id = None
    request.user.talantuser.save()

    return redirect('user_page')


@login_required
def logout_page(request):
    logout(request)
    return redirect('index')


@login_required
def analyse_page(request):
    return render(request, 'analyse.html', {'user': request.user})


@login_required
def dota_analyse(request):
    ctx = {}

    if request.method == 'POST':
        user = request.user

        if user.talantuser.dota_process or user.talantuser.steam_id is None:
            ctx['error'] = "Приыяжите Steam к аккаунту"
            return JsonResponse(ctx)

        task = tasks.dota_count.delay(user.pk)
        user.talantuser.dota_task = task.id
        user.talantuser.save()

        ctx['task_id'] = task.id

    return JsonResponse(ctx)


def task_status(request, task_id):
    ctx = {}
    task = current_app.AsyncResult(task_id)
    ctx['status'] = task.status

    if task.status == 'SUCCESS':
        ctx['result'] = task.get()

    return JsonResponse(ctx)
