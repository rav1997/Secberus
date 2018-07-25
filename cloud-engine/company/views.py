# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from rest_framework import status
from django.shortcuts import render
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response

from secberusAPI.settings import client

class ListCompanies(GenericAPIView):

    def get(self, request, format='json'):
        user = self.request.user.id
        query_line = "For data IN UserCompanies\
                    FILTER data.user == "+str(user)+" For obj IN Companies\
                        FILTER obj._id == data.company\
                        RETURN {'id': obj._id ,'name': obj.name}"
        q = client.api.cursor().post({"query": query_line})
        if q['code'] == 201:
            return Response(q['result'], status=status.HTTP_201_CREATED)
        else:
            return Response(q['result'], status=status.HTTP_400_BAD_REQUEST)
