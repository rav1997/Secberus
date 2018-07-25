from __future__ import unicode_literals

import requests
import json

import urllib
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from datetime import datetime
from rest_framework import serializers
from .models import AwsCredentials, ScheduleIntervalSettings
from company.models import Companies
from arangodb.query.simple import SimpleQuery
from arangodb.api import Collection
from secberusAPI.constants import FOXX_BASE_URL

class CredentialSerializer(serializers.Serializer):
    role_arn = serializers.CharField(required=True)
    external_id  = serializers.CharField(required=True)
    account_name = serializers.CharField(required=True)

    # Custom validation for unique RoleArn and
    # Unique account name in company
    def validate(self, data):
        collection = Collection.get_loaded_collection(name='AwsCredentials')
        obj = SimpleQuery.get_by_example(collection, example_data={
            'company': self.context['company'],
            'external_id': data['external_id']})
        if obj:
            raise serializers.ValidationError("External id already exist for a company")

        obj = SimpleQuery.get_by_example(collection, example_data={
            'company': self.context['company'],
            'role_arn': data['role_arn']})
        if obj:
            raise serializers.ValidationError("Role Arn already exist")

        obj = SimpleQuery.get_by_example(collection, example_data={
            'company': self.context['company'],
            'account_name': data['account_name']})
        if obj:
            raise serializers.ValidationError("Account name already exist for a company")
        return data

    def create(self, validated_data):
        #Init Arango Models
        AwsCredentials.init()
        Companies.init()

        obj = AwsCredentials()
        obj.role_arn = str(validated_data['role_arn'])
        obj.external_id = str(validated_data['external_id'])
        obj.account_name = str(validated_data['account_name'])
        obj.company = Companies.objects.get(_id=str(self.context['company']))
        obj.user = int(self.context['user'])
        obj.save()
        collection = Collection.get_loaded_collection('AwsExternalIds')
        SimpleQuery.update_by_example(collection, {
            'external_id': obj.external_id
        }, {'used': True, 'company': str(obj.company.id), 'user': obj.user})
        return obj.id

class IntervalSetting(serializers.Serializer):
    account_id = serializers.CharField(required=True)
    service  = serializers.CharField(required=True)
    repeat_delay = serializers.IntegerField(required=True)

    # Custom validation to check a setting document exist.
    def validate(self, data):
        collection = Collection.get_loaded_collection(name='ScheduleIntervalSettings')
        obj = SimpleQuery.get_by_example(collection, example_data={
            'account_id': str(data['account_id']),
            'service': str(data['service']),
        })
        if obj:
            raise serializers.ValidationError("A setting for the given service already exist with the account")

        AwsCredentials.init()
        Companies.init()
        aws_obj = AwsCredentials.objects.get(_id=str(data['account_id']))
        if str(aws_obj.company.id) != str(self.context['company']):
            raise serializers.ValidationError('Companies account are different for Aws and currenly logged in User')

        return data

    def create(self, validated_data):
        #Init Arango Models
        ScheduleIntervalSettings.init()
        AwsCredentials.init()
        Companies.init()

        obj = ScheduleIntervalSettings()
        obj.account_id = AwsCredentials.objects.get(_id=str(validated_data['account_id']))
        print(str(validated_data['service']))
        obj.service = str(validated_data['service'])
        print(obj)
        obj.repeat_delay = int(validated_data['repeat_delay'])
        obj.user = int(self.context['user'])
        obj.save()
        return obj.id


class EditInterval(serializers.Serializer):
    account_id = serializers.CharField(required=True)
    service  = serializers.CharField(required=True)
    repeat_delay = serializers.IntegerField(required=True)

    # Custom validation to check a setting document exist.
    def validate(self, data):
        collection = Collection.get_loaded_collection(name='ScheduleIntervalSettings')
        obj = SimpleQuery.get_by_example(collection, example_data={
            'account_id': str(data['account_id']),
            'service': str(data['service']),
        })
        if not obj:
            raise serializers.ValidationError("A setting for the given service with this account not exist")

        AwsCredentials.init()
        Companies.init()
        aws_obj = AwsCredentials.objects.get(_id=str(data['account_id']))
        if str(aws_obj.company.id) != str(self.context['company']):
            raise serializers.ValidationError('Companies account are different for Aws and currenly logged in User')

        return data

    def create(self, validated_data):
        #Init Arango Models
        AwsCredentials.init()
        Companies.init()
        account_obj = AwsCredentials.objects.get(_id=str(validated_data['account_id']))
        obj = Collection.get_loaded_collection(name='ScheduleIntervalSettings')
        SimpleQuery.update_by_example(obj, {
            'account_id': str(account_obj.document),
            'service': str(validated_data['service']),
        }, {'service': validated_data['service'], 'repeat_delay': validated_data['repeat_delay']})
        response = SimpleQuery.get_by_example(obj, example_data={
            'account_id': str(account_obj.document),
            'service': str(validated_data['service'])
        })
        headers = {"Content-Type": "application/json"}
        url = FOXX_BASE_URL+"execute/"+urllib.quote_plus(str(response))+"/"+str(self.context['user'])+"/edit"
        response = requests.get(url, headers=headers)
        return response
