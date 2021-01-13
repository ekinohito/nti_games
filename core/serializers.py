from rest_framework import serializers
from django.contrib.auth.models import User
from .models import TalantUser


class CurrentUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            # 'username',
            'email',
            'id',
            'first_name',
            'last_name'
        )


class TalentUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = TalantUser
        fields = (
            'pk',
            'dota_result', 'cs_result',
            'dota_task', 'cs_task'
        )
