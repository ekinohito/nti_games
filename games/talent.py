from dataclasses import dataclass

from django.conf import settings
from authlib.integrations.requests_client import OAuth2Session

client_id = settings.TALANT_CLIENT_ID
client_secret = settings.TALANT_CLIENT_SECRET
redirect_uri = 'http://localhost:8000/auth/'
authorization_endpoint = 'https://talent.kruzhok.org/oauth/authorize/'
token_endpoint = 'https://talent.kruzhok.org/api/oauth/issue-token/'


@dataclass
class TalentInfo:
    id: int
    email: str
    first_name: str
    last_name: str


def get_oauth_sess(token=None, token_endpoint_auth_method='client_secret_post'):
    return OAuth2Session(client_id, client_secret, token=token, token_endpoint_auth_method=token_endpoint_auth_method)


def get_talent_info(token) -> TalentInfo:
    client = OAuth2Session(client_id, client_secret, token=token)
    # id, email, first_name, last_name
    resp = client.get('https://talent.kruzhok.org/api/user/').json()
    return TalentInfo(id=resp['id'], email=resp['email'], first_name=resp['first_name'], last_name=resp['last_name'])
