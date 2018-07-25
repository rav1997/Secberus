# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import datetime
from django.db import models
from django.contrib import auth
from django.contrib.auth.models import User
from arangodb.orm.models import CollectionModel
from arangodb.orm.fields import CharField, NumberField, DatetimeField
from .utils import company

class UserProfiles(CollectionModel):
    user = NumberField(required=True)
    phone_number = CharField(required=True)
    country = CharField(required=True)
    state = CharField(required=True)
    role = CharField(required=True)
    created_on =  DatetimeField(default=datetime.datetime.now())

auth.models.User.add_to_class('company', company)
