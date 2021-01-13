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
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from . import serializers

from .models import TalantUser
from . import talent
from . import tasks


class CurrentUserView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = serializers.CurrentUserSerializer(request.user)
        return Response(serializer.data)


class CurrentTalentUserView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = serializers.TalentUserSerializer(request.user.talantuser)
        return Response(serializer.data)


class AuthLoginTalent(APIView):
    def get(self, request):
        redirect_uri = generate_uri(request, reverse('api_auth_complete_talent'))

        uri, state = talent.OAuth2Session(talent.client_id, talent.client_secret).create_authorization_url(
            talent.authorization_endpoint, response_type='code',
            nonce=time.time(), redirect_uri=redirect_uri
        )
        return redirect(uri)


class AuthCompleteTalent(APIView):
    def get(self, request):
        #  GET
        #  '/auth/?error=access_denied&error_description=The+resource+owner+or+authorization+server+denied+the+request'
        if request.query_params.get('error'):
            return redirect('index')

        token = requests.post(talent.token_endpoint, data={
            'grant_type': 'authorization_code',
            'scope': 'openid',
            'nonce': time.time(),
            'client_id': talent.client_id,
            'client_secret': talent.client_secret,
            'redirect_uri': generate_uri(request, reverse('api_auth_complete_talent')),
            'code': request.query_params['code'],
        }).json()

        user_info = talent.get_talent_info(token)
        if not User.objects.filter(email=user_info.email).exists():
            register_user(user_info, token)

        user = authenticate(request, email=user_info.email)

        if user is not None:
            login(request, user)
            return redirect('user_page')

        return redirect('index')


class LogoutTalent(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        logout(request)
        return redirect('index')


class AuthLoginSteam(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        redirect_uri = generate_uri(request, reverse('steam_auth'))
        params = {
            'openid.ns': settings.OPEN_ID_NS,
            'openid.identity': settings.OPEN_ID_IDENTITY,
            'openid.claimed_id': settings.OPEN_ID_CLAIMED_ID,
            'openid.mode': 'checkid_setup',
            'openid.return_to': redirect_uri,
            'openid.realm': generate_uri(request, reverse('index')),
        }

        auth_url = settings.FORMAT_STEAM_AUTH_URL.format(urlencode(params))
        return redirect(auth_url)


class AuthCompleteSteam(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        request.user.talantuser.steam_openid = request.query_params['openid.identity']
        request.user.talantuser.steam_id = int(request.query_params['openid.identity'].split('/')[-1])
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


class LogoutSteam(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        request.user.talantuser.steam_openid = ''
        request.user.talantuser.steam_id = None
        request.user.talantuser.save()

        return redirect('user_page')


def index_page(request):
    return render(request, 'core/index.html')


@login_required
def user_page(request):
    return render(request, 'core/user_page.html', {'user': request.user})


def register_user(talent_info: talent.TalentInfo, token):
    user = User(email=talent_info.email, username=talent_info.email, first_name=talent_info.first_name,
                last_name=talent_info.last_name)
    user.save()
    talent_user = TalantUser(user=user, access_token=json.dumps(token))
    talent_user.save()


@login_required
def analyse_page(request):
    return render(request, 'core/analyse.html', {
        'user': request.user,
        'dota_result': None if request.user.talantuser.dota_result is None else json.loads(
            request.user.talantuser.dota_result),
        'cs_result': None if request.user.talantuser.cs_result is None else json.loads(
            request.user.talantuser.cs_result),
    })


@login_required
def dota_analyse(request):
    ctx = {}

    if request.method == 'POST':
        user = request.user

        if user.talantuser.steam_id is None:
            ctx['error'] = "Привяжите Steam к аккаунту"
            return JsonResponse(ctx)
        if user.talantuser.dota_task:
            ctx['error'] = 'Задача уже в очереди'
            return JsonResponse(ctx)

        task = tasks.dota_count.delay(user.pk)
        user.talantuser.dota_task = task.id
        user.talantuser.save()

        ctx['task_id'] = task.id

    return JsonResponse(ctx)


@login_required
def cs_analyse(request):
    ctx = {}

    if request.method == 'POST':
        user = request.user

        if user.talantuser.steam_id is None:
            ctx['error'] = "Привяжите Steam к аккаунту"
            return JsonResponse(ctx)
        if user.talantuser.cs_task:
            ctx['error'] = 'Задача уже в очереди'
            return JsonResponse(ctx)

        task = tasks.cs_count.delay(user.pk)
        user.talantuser.cs_task = task.id
        user.talantuser.save()

        ctx['task_id'] = task.id

    return JsonResponse(ctx)


@login_required
def task_status(request, task_id):
    ctx = {}
    task = current_app.AsyncResult(task_id)
    ctx['status'] = task.status

    if task.status == 'SUCCESS':
        ctx['result'] = task.get()
    if task.status == 'FAILURE':
        ctx['error'] = str(task.result)

    return JsonResponse(ctx)


def generate_uri(request, rev):
    uri = request.build_absolute_uri(rev)
    if settings.HTTPS_ONLY:
        uri = uri.replace('http', 'https')

    return uri
