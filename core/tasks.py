import json

from celery import shared_task
from django.contrib.auth.models import User
from .models import TalantUser, DotaResult, CsResult
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
        result = DotaResult(error=e, result=None)
        result.save()

        user.talantuser.dota_task = ''
        user.talantuser.dota_result = result
        user.talantuser.save()

        raise e

    result = DotaResult(error=None, result=json.dumps(res))
    result.save()

    user.talantuser.dota_task = None
    user.talantuser.dota_result = result
    user.talantuser.save()


@shared_task
def cs_count(user_id: int):
    user = User.objects.get(pk=user_id)
    steam_id = user.talantuser.steam_id

    cs = CSGOAnalysing(settings.STEAM_API_KEY, steam_id)
    try:
        res = cs.start()
    except Exception as e:
        result = CsResult(error=e, result=None)
        result.save()

        user.talantuser.cs_task = None
        user.talantuser.cs_result = result
        user.talantuser.save()

        raise e

    result = CsResult(error=None, result=json.dumps(res))
    result.save()

    user.talantuser.cs_task = ''
    user.talantuser.cs_result = result
    user.talantuser.save()
