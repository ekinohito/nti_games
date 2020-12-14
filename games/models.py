from django.db import models
from django.contrib.auth.models import User


class TalantUser(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    access_token = models.CharField(max_length=2500)

    steam_openid = models.CharField(max_length=200, default='')
    steam_id = models.BigIntegerField(default=0)
    # talant
