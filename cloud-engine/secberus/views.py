# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import datetime
from rest_framework.views import APIView
from rest_framework.generics import GenericAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.template.loader import render_to_string
from django.core.mail import EmailMessage
from django.contrib.sites.shortcuts import get_current_site
from django.contrib.auth.models import User
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_text
from django.core.urlresolvers import reverse


from .serializers import UserSerializer, ForgetPasswordSerializer, ChangePasswordSerializer, ActivationResendSerializer
from secberus.utils import send_email, jwt_token, current_site_url
from secberus.token import account_activation_token
from secberusAPI.constants import (
    ACTIVATION_EMAIL_RESET_TIMEOUT, REGISTRATION_ACTIVATION_EMAIL_SUBJECT,
    WELCOME_EMAIL_SUBJECT, TERMS_URL, DOCUMENTATION_URL,
    PASSWORD_RESET_EMAIL_SUBJECT, TRIAL_PERIOD_ACCESS, FRONT_END_URL
    )
from django.db import transaction

# Create your views here.
class UserCreate(GenericAPIView):
    """
        AllowAny: Skip token validation and
        Providing access to register in application
    """
    serializer_class = UserSerializer

    permission_classes = (AllowAny,)
    @transaction.atomic
    def post(self, request, format='json'):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            if user:
                send_email(to=user.email,
                            template="email/register_confirmation.html",
                            template_data={
                                'user_name': user.get_full_name,
                                'domain': FRONT_END_URL,
                                'uid':urlsafe_base64_encode(force_bytes(user.pk)),
                                'token':account_activation_token.make_token(user),
                                'trial_expire': ACTIVATION_EMAIL_RESET_TIMEOUT
                            }, subject=REGISTRATION_ACTIVATION_EMAIL_SUBJECT)
                return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response({
            "items": serializer.errors,
            "message": "Unable to create user",
            }, status=status.HTTP_400_BAD_REQUEST)

class LogOut(APIView):
    def get(self, request, format='json'):
        """
        API View that receives a GET request.
        And logout the user from currenly logged in session.
        """

        self.request.session.flush()
        return Response(status=status.HTTP_200_OK)

class AccountActivate(APIView):
    permission_classes = (AllowAny,)

    def get(self, request, uidb64, token, format='json'):
        """
        API View that receives a GET request with uid and token passed as URL parameter.
        Verify the authentication and returns the JWT token.
        """

        try:
            uid = force_text(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)
        except(TypeError, ValueError, OverflowError, User.DoesNotExist):
            user = None

        if user is not None and account_activation_token.check_token(user, token):
            user.is_active = True
            user.date_joined = datetime.datetime.now()
            user.save()
            send_email(to=user.email,
                template="email/welcome_email.html",
                template_data={
                    'user_name': user.get_full_name,
                    'domain': FRONT_END_URL,
                    'terms_url': get_current_site(request).domain+"/"+TERMS_URL,
                    'docs_url': get_current_site(request).domain+"/"+DOCUMENTATION_URL,
                    'trial_expire': (user.date_joined+datetime.timedelta(days=TRIAL_PERIOD_ACCESS)).strftime('%d-%m-%Y')
                }, subject=WELCOME_EMAIL_SUBJECT)
            return Response({'token': jwt_token(user)}, status=status.HTTP_201_CREATED)
        else:

            return Response({
                "items": {},
                "message": "Invalid token string passed",
                }, status=status.HTTP_401_UNAUTHORIZED)

class ForgetPasswordView(GenericAPIView):
    serializer_class = ForgetPasswordSerializer
    permission_classes = (AllowAny, )

    def post(self, request):
        serializer = ForgetPasswordSerializer(data=request.data)
        if serializer.is_valid():
            user = User.objects.get(email = serializer.data['email'])

            send_email(to=user.email,
                        template="email/forget_password_email.html",
                        template_data={
                                    'user_name': user.get_full_name,
                                    'domain': FRONT_END_URL,
                                    'uid':urlsafe_base64_encode(force_bytes(user.pk)),
                                    'token':account_activation_token.make_token(user),
                                    'trial_expire': ACTIVATION_EMAIL_RESET_TIMEOUT
                                }, subject=PASSWORD_RESET_EMAIL_SUBJECT)
            return Response({'msg' : 'We send you an Link to change your password'}, status=status.HTTP_201_CREATED)
        return Response({
            "items": serializer.errors,
            "message": "Error in perform forgot password",
            }, status=status.HTTP_400_BAD_REQUEST)

class PasswordChangeView(GenericAPIView):
    serializer_class = ChangePasswordSerializer
    permission_classes = (AllowAny,)

    def post(self, request, format='json'):
        """
        API View that Changes the password of User
        """
        serializer = ChangePasswordSerializer(data=request.data)
        if serializer.is_valid():
            uidb64 = request.data.get('uidb64')
            password = request.data.get('new_password')
            confirm_password = request.data.get('confirm_password')
            token = request.data.get('token')
            try:
                uid = force_text(urlsafe_base64_decode(uidb64))
                user = User.objects.get(pk=uid)
            except(TypeError, ValueError, OverflowError, User.DoesNotExist):
                user = None

            if user is not None and account_activation_token.check_token(user, token):
                    user.set_password(password)
                    user.save()
                    return Response({'message': "Successfully Updated the password"}, status=status.HTTP_201_CREATED)
            else:
                return Response({'message': 'Unauthorized'}, status=status.HTTP_401_UNAUTHORIZED)
        return Response({
            "items": serializer.errors,
            "message": "Error in changing password",
            }, status=status.HTTP_400_BAD_REQUEST)

class ActivationEmailResend(GenericAPIView):
    
    serializer_class =  ActivationResendSerializer
    permission_classes = (AllowAny, )

    def post(self, request):
        serializer = ActivationResendSerializer(data=request.data)
        if serializer.is_valid():
            try:
                user = User.objects.get(email = serializer.data['email'])
            except(User.DoesNotExist):
                user = None

            if user:
                if user.is_active:
                    return Response({
                        "items": [],
                        "message": "Already Activated",
                        }, status=status.HTTP_400_BAD_REQUEST)
                else:
                    send_email(to=user.email,
                            template="email/register_confirmation.html",
                            template_data={
                                'user_name': user.get_full_name,
                                'domain': get_current_site(self.request).domain,
                                'uid':urlsafe_base64_encode(force_bytes(user.pk)),
                                'token':account_activation_token.make_token(user),
                                'trial_expire': ACTIVATION_EMAIL_RESET_TIMEOUT
                                }, subject=REGISTRATION_ACTIVATION_EMAIL_SUBJECT)
                    return Response({
                            "items": [],
                            "message": "Activation Email Resend",
                            }, status=status.HTTP_201_CREATED)
        else:
            return Response({
                "items": serializer.errors,
                "message": "Unauthorized",
                }, status=status.HTTP_401_UNAUTHORIZED)
            
