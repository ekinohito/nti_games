from django.conf import settings


def generate_uri(request, rev):
    uri = request.build_absolute_uri(rev)
    if settings.HTTPS_ONLY:
        uri = uri.replace('http', 'https')

    return uri
