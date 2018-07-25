from __future__ import unicode_literals

import requests
import json
import jwt

from django.template.loader import render_to_string
from django.core.mail import EmailMultiAlternatives, EmailMessage
from django.conf import settings
from django.contrib.auth.models import User

from secberusAPI.constants import EMAIL_SUBJECT, EMAIL_FROM
from rest_framework_jwt.settings import api_settings
from rest_framework_jwt.settings import api_settings
from rest_framework.views import exception_handler

from arangodb.api import Collection
from arangodb.query.simple import SimpleQuery

jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER

requests.packages.urllib3.disable_warnings()

def jwt_token(user):
    jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
    jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER
    payload = jwt_payload_handler(user)
    return jwt_encode_handler(payload)

def send_email(to, template, template_data={}, subject=EMAIL_SUBJECT,from_email=EMAIL_FROM):
    message = render_to_string(template, template_data)
    email_to = to if isinstance(to, list) else to.split()
    msg = EmailMultiAlternatives(subject, '', from_email, email_to)
    msg.attach_alternative(message, "text/html")
    msg.send()

def current_site_url(request):
    protocol = getattr(settings, 'MY_SITE_PROTOCOL', 'http')
    return protocol+"://"+request.get_host()

def company(self):
    collection = Collection.get_loaded_collection(name='UserCompanies')
    obj = SimpleQuery.get_by_example(collection, example_data={
        'user': int(self.id),
        'active': True
    })
    return obj.company

def get_default_role():
    obj = Collection.get_loaded_collection(name='Roles')
    return SimpleQuery.get_by_example(obj, example_data={
        'slug': 'user'
    })
