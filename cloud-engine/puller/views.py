# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import requests
import json

from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from rest_framework import status

from django.shortcuts import render
from .serializers import PullerSerializer
from arangodb.api import Collection
from aws.models import AwsCredentials
from secberusAPI.constants import FOXX_BASE_URL
from company.models import Companies

class Pull(GenericAPIView):
    serializer_class = PullerSerializer
    def post(self, request, format='json'):
        """
            API View that receives a POST with a role_arn, external_id, service and user id.
            It validates the given url hits the aws puller.
        """
        serializer = PullerSerializer(data=request.data, context={
                'company': self.request.user.company()
                })
        if serializer.is_valid():
            try:
                AwsCredentials.init()
                Companies.init()
                obj = AwsCredentials.objects.get(_id=str(request.data['account_id']))
                data, headers = {
                    'external_id': obj.external_id,
                    'role_arn': obj.role_arn,
                    'service': request.data['service'],
                    'user': self.request.user.id,
                    'account_id': obj.id
                }, {
                    'content-type': 'application/json',
                }
                url = FOXX_BASE_URL+"puller"
                response = requests.post(url, headers=headers, data=json.dumps(data))
                return Response(response.content, status=status.HTTP_201_CREATED)
            except Exception as e:
                return Response({
                    "items": {},
                    "message": str(e),
                    }, status=status.HTTP_400_BAD_REQUEST)
        return Response({
            "items": serializer.errors,
            "message": "Unable to Pull",
            }, status=status.HTTP_400_BAD_REQUEST)
