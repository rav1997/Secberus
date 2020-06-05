# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2018-06-04 07:20
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('aws', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='credential',
            name='account_name',
            field=models.CharField(max_length=100),
        ),
        migrations.AlterField(
            model_name='credential',
            name='external_id',
            field=models.CharField(max_length=70),
        ),
        migrations.AlterField(
            model_name='credential',
            name='role_arn',
            field=models.CharField(max_length=50),
        ),
    ]