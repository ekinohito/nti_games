import json

from django.contrib.auth.decorators import login_required
from django.shortcuts import render


def index_page(request):
    return render(request, 'core/index.html')


@login_required
def user_page(request):
    return render(request, 'core/user_page.html', {'user': request.user})


@login_required
def analyse_page(request):
    return render(request, 'core/analyse.html', {
        'user': request.user,
        'dota_result': None if (request.user.talantuser.dota_result.result is None
                                or request.user.talantuser.dota_result.error) else
        json.loads(request.user.talantuser.dota_result.result),
        'cs_result': None if (request.user.talantuser.cs_result.result is None
                              or request.user.talantuser.cs_result.error) else
        json.loads(request.user.talantuser.cs_result.result),
    })
