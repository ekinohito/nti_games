import json

from celery import shared_task
from django.contrib.auth.models import User
from .models import DotaResult, CsResult
from django.conf import settings

from analytics.dota.algo_dota import DotaAnalysing
from analytics.cs_go.algo_cs_go import CSGOAnalysing


@shared_task
def dota_count(user_id: int):
    user = User.objects.get(pk=user_id)
    steam_id = user.talantuser.steam_id

    dota = DotaAnalysing(steam_id)
    try:
        res = dota.start()
    except Exception as e:
        user.talantuser.dota_task = None
        user.talantuser.dota_result.error = e
        user.talantuser.dota_result.result = None

        user.talantuser.dota_result.save()
        user.talantuser.save()

        raise e

    user.talantuser.dota_task = None
    user.talantuser.dota_result.error = None
    user.talantuser.dota_result.result = json.dumps(res)

    user.talantuser.dota_result.save()
    user.talantuser.save()


@shared_task
def cs_count(user_id: int):
    user = User.objects.get(pk=user_id)
    steam_id = user.talantuser.steam_id

    cs = CSGOAnalysing(settings.STEAM_API_KEY, steam_id)
    try:
        res = cs.start()
    except Exception as e:
        user.talantuser.cs_task = None
        user.talantuser.cs_result.result = None
        user.talantuser.cs_result.error = e

        user.talantuser.cs_result.save()
        user.talantuser.save()

        raise e

    user.talantuser.cs_task = ''
    user.talantuser.cs_result.result = json.dumps(res)
    user.talantuser.cs_result.error = None

    user.talantuser.cs_result.save()
    user.talantuser.save()
