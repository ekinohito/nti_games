from django.conf import settings
from django.shortcuts import redirect
from rest_framework.decorators import api_view


@api_view()
def schema_view(request):
    return redirect('/static/core/schema.yml')


def generate_uri(request, rev):
    uri = request.build_absolute_uri(rev)
    if settings.HTTPS_ONLY:
        uri = uri.replace('http', 'https')

    return uri
