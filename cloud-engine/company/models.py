# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import datetime

from arangodb.orm.models import CollectionModel
from arangodb.orm.fields import CharField, DatetimeField

class Companies(CollectionModel):
    name = CharField(required=True)
    created_on = DatetimeField(default=datetime.datetime.now())
