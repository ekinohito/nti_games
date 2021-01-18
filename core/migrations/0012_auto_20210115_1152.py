# Generated by Django 3.1.4 on 2021-01-15 11:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0011_auto_20210114_1437'),
    ]

    operations = [
        migrations.AddField(
            model_name='talantuser',
            name='blizzard_access_token',
            field=models.CharField(default=None, max_length=2500, null=True),
        ),
        migrations.AddField(
            model_name='talantuser',
            name='blizzard_battletag',
            field=models.CharField(default=None, max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='talantuser',
            name='blizzard_id',
            field=models.BigIntegerField(default=None, null=True),
        ),
    ]
