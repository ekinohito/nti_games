import json

from celery import shared_task
from django.contrib.auth.models import User
from django.conf import settings

from dota.algo_dota import DotaAnalysing
from cs_go.algo_cs_go import  CSGOAnalysing


@shared_task
def adding_task(x, y):
    return x + y


@shared_task
def dota_count(user_id: int):
    user = User.objects.get(pk=user_id)
    steam_id = user.talantuser.steam_id

    dota = DotaAnalysing(steam_id)
    try:
        res = dota.start()
    except Exception as e:
        user.talantuser.dota_result = None
        user.talantuser.dota_task = ''
        user.talantuser.save()

        raise e

    user.talantuser.dota_result = json.dumps(res)
    user.talantuser.dota_task = ''
    user.talantuser.save()

    return res


@shared_task
def cs_count(user_id: int):
    user = User.objects.get(pk=user_id)
    steam_id = user.talantuser.steam_id

    cs = CSGOAnalysing(settings.STEAM_API_KEY, steam_id)
    try:
        res = cs.start()
    except Exception as e:
        user.talantuser.cs_result = None
        user.talantuser.cs_task = ''
        user.talantuser.save()

        raise e

    user.talantuser.cs_result = json.dumps(res)
    user.talantuser.cs_task = ''
    user.talantuser.save()

    return res
    pass
