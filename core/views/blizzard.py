import json

from django.shortcuts import redirect
from django.urls import reverse
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from authlib.integrations.django_client import OAuth

from core.views.utils import generate_uri

BLIZZARD_CONF_URL = 'https://eu.battle.net/oauth/.well-known/openid-configuration'
oauth = OAuth()
oauth.register(
    name='blizzard',
    server_metadata_url=BLIZZARD_CONF_URL,
    client_kwargs={
        'scope': ''
    }
)


class AuthLoginBlizzard(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        redirect_uri = generate_uri(request, reverse('blizzard_auth'))
        return oauth.blizzard.authorize_redirect(request, redirect_uri)


class AuthCompleteBlizzard(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        token = oauth.blizzard.authorize_access_token(request)
        user_info = oauth.blizzard.request('get', 'https://eu.battle.net/oauth/userinfo',
                                           token=token).json()  # sub, id, battletag
        request.user.talantuser.blizzard_access_token = json.dumps(token)
        request.user.talantuser.blizzard_battletag = user_info['battletag']
        request.user.talantuser.blizzard_id = user_info['id']
        request.user.talantuser.save()

        return redirect('user_page')


class LogoutBlizzard(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        request.user.talantuser.blizzard_access_token = None
        request.user.talantuser.blizzard_battletag = None
        request.user.talantuser.blizzard_id = None
        request.user.talantuser.save()

        return redirect('user_page')
