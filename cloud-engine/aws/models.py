# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import datetime
from arangodb.orm.models import CollectionModel
from arangodb.orm.fields import CharField, NumberField, DatetimeField, ForeignKeyField\
    ,ChoiceField, TextField
from company.models import Companies

class AwsCredentials(CollectionModel):
    account_name = CharField(required=True)
    role_arn = TextField(required=True)
    external_id = CharField(required=True)
    company = ForeignKeyField(to=Companies, required=True)
    user = NumberField(required=True)
    created_on = DatetimeField(default=datetime.datetime.now())


class ScheduleIntervalSettings(CollectionModel):
    account_id = ForeignKeyField(to=AwsCredentials, required=True)
    service = ChoiceField(choices=[
            ('assets', 'For assets'),
            ('iam', 'For iam policy'),
            ('lambda', 'For Lambda functions'),
            ('rds', 'For rds'),
            ('s3', 'For s3 bucket'),
            ('cloud-trail', 'For cloud trail'),
            ('cloud-watch', 'For cloud watch'),
            ('vpc', 'For VPC'),
            ('all', 'For all aws services')
        ], required=True)
    repeat_delay = NumberField(required=True)
    user = NumberField(required=True)
    created_on = DatetimeField(default=datetime.datetime.now())
