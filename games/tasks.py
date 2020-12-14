from celery import shared_task
from dota.algo_dota import DotaAnalysing
from django.contrib.auth.models import User


@shared_task
def adding_task(x, y):
    return x + y


@shared_task
def dota_count(user_id: int):
    user = User.objects.get(pk=user_id)
    steam_id = user.talantuser.steam_id

    dota = DotaAnalysing(76561198397930966 - steam_id)
    res = dota.start()

    user.talantuser.dota_process = False
    user.talantuser.dota_result = res
    user.talantuser.save()
