# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import requests
import json
import urllib
import random

from arangodb.api import Collection, Document
from arangodb.query.simple import SimpleQuery
from secberusAPI.settings import client

from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from rest_framework import status
from django import forms

from .serializers import CredentialSerializer, IntervalSetting, EditInterval
from .creds_verifier import aws_creds_verifier
from secberusAPI.constants import FOXX_BASE_URL

class SaveCredential(GenericAPIView):

    serializer_class = CredentialSerializer

    def post(self, request, format='json'):
        """
            API View that receives a POST with a role_arn, external_id and account_name.
            It validates the given aws Credentials and saved them.
        """
        company = self.request.user.company()
        user = self.request.user
        serializer = CredentialSerializer(data=request.data, context={
                'company': company,
                'user': user.id
        })
        if serializer.is_valid():
            result = aws_creds_verifier(request.data['role_arn'], request.data['external_id'], self.request.user.id)
            if result['code'] == 200:
                response = serializer.save()
                return Response({'id': response}, status=status.HTTP_201_CREATED)
            else:
                return Response({
                    "items": {},
                    "message": result['msg'],
                    }, status=status.HTTP_400_BAD_REQUEST)
        return Response({
            "items": serializer.errors,
            "message": "Unable to create aws account",
            }, status=status.HTTP_400_BAD_REQUEST)

class ScheduleIntervalSetting(GenericAPIView):

    serializer_class = IntervalSetting

    def post(self, request, format='json'):
        """
            API View that receives a POST.
        """
        serializer = IntervalSetting(data=request.data, context={
                'user': self.request.user.id,
                'company': self.request.user.company()
                })
        if serializer.is_valid():
            try:
                obj = serializer.save()
                headers = {'content-type': 'application/json'}
                url = FOXX_BASE_URL+"execute/"+urllib.quote_plus(obj)+"/"+str(self.request.user.id)+"/new"
                response = requests.get(url, headers=headers)
                return Response(response, status=status.HTTP_201_CREATED)
            except Exception as e:
                return Response({
                    "items": {},
                    "message": str(e),
                    }, status=status.HTTP_400_BAD_REQUEST)
        return Response({
            "items": serializer.errors,
            "message": "Unable to schedule interval setting",
            }, status=status.HTTP_400_BAD_REQUEST)

class EditIntervalSetting(GenericAPIView):

    serializer_class = EditInterval

    def post(self, request, format='json'):
        """
            API View that receives a POST.
        """
        serializer = EditInterval(data=request.data, context={
                'user': self.request.user.id,
                'company': self.request.user.company()
                })
        if serializer.is_valid():
            response = serializer.save()
            return Response(response, status=status.HTTP_201_CREATED)
        return Response({
            "items": serializer.errors,
            "message": "Unable to edit interval settings",
            }, status=status.HTTP_400_BAD_REQUEST)

class GetExternalId(GenericAPIView):

    def get(self, request, format='json'):
        """
            API View that receives a GET request.
            and will return a single random unused external id.
        """
        obj = Collection.get_loaded_collection(name='AwsExternalIds')
        document = SimpleQuery.get_by_example(obj, example_data={
            'used': False,
        },allow_multiple=True)
        if document:
            external_id = Document(
                random.choice(document),
                '', 'AwsExternalIds', client.api
            ).retrieve()['external_id']
        else:
            external_id = "Not found"
        return Response(external_id, status=status.HTTP_201_CREATED)


class ListAccounts(GenericAPIView):

    def get(self, request, format='json'):
        company = self.request.user.company()
        query_line = "For data IN AwsCredentials\
                    FILTER data.company == '"+str(company)+"' RETURN\
                    {'id': data._id,'account_name': data.account_name,'role_arn': data.role_arn,\
                    'external_id': data.external_id, 'created_on' : data.created_on}"
        q = client.api.cursor().post({"query": query_line})
        if q['code'] == 201:
            return Response(q['result'], status=status.HTTP_201_CREATED)
        else:
            return Response(q['result'], status=status.HTTP_400_BAD_REQUEST)
