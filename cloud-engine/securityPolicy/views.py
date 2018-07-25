# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from rest_framework import status
from django.shortcuts import render
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from .serializers import ListPolicySerializer, PolicyRuleSerializer

from secberusAPI.settings import client

class ListPolicy(GenericAPIView):
    serializer_class = ListPolicySerializer

    def post(self, request, format='json'):
        """
            Post request that accepts Aws Account Id as a post parameter
            And return the security policies with the rules attach to it
        """
        serializer = ListPolicySerializer(data=request.data)
        user, error = self.request.user.id, 'Error in getting security policy'
        if serializer.is_valid():
            try:
                query_line = "For data IN SecurityPolicies\
                                FILTER data.account_id == '"+str(request.data['account_id'])+"'\
                                RETURN data"
                q = client.api.cursor().post({"query": query_line})
                if q['code'] == 201:
                    for data in q['result']:
                        for rule in data['rules']:
                            query_line = "For data IN Rules\
                                            FILTER data._id == '"+str(rule['rule_id'])+"'\
                                            RETURN data.name"
                            rule['rule_name'] = client.api.cursor().post({"query": query_line})['result'][0]
                    return Response(q['result'], status=status.HTTP_201_CREATED)
                else:
                    error = q['result']
            except Exception as e:
                error = str(e)
        return Response({
            "items": serializer.errors,
            "message": error,
        }, status=status.HTTP_400_BAD_REQUEST)


class ListRules(GenericAPIView):
    serializer_class = PolicyRuleSerializer

    def post(self, request, format='json'):
        """
            Post request that accepts Security Policy Id as a post parameter
            And return the rules dictionary attach to the policy
        """
        serializer = PolicyRuleSerializer(data=request.data)
        user, error = self.request.user.id, 'Error in getting security policy'
        if serializer.is_valid():
            try:
                query_line = "For data IN SecurityPolicies\
                                FILTER data._id == '"+str(request.data['security_policy_id'])+"'\
                                RETURN data.rules"
                q = client.api.cursor().post({"query": query_line})
                if q['code'] == 201:
                    for data in q['result'][0]:
                        query_line = "For data IN Rules\
                                        FILTER data._id == '"+str(data['rule_id'])+"'\
                                        RETURN data"
                        rule_obj = client.api.cursor().post({"query": query_line})
                        if rule_obj['code'] == 201:
                            for rule in rule_obj['result']:
                                for key, value in rule.items():
                                    data[key] = value

                    return Response(q['result'][0], status=status.HTTP_201_CREATED)
                else:
                    error = q['result']
            except Exception as e:
                error = str(e)
        return Response({
            "items": serializer.errors,
            "message": error,
        }, status=status.HTTP_400_BAD_REQUEST)
