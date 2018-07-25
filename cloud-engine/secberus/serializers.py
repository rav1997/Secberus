from django.contrib.auth.models import User
from django.contrib.auth import authenticate

import datetime
from rest_framework import serializers
from rest_framework.validators import UniqueValidator, UniqueTogetherValidator
from company.models import Companies
from .models import UserProfiles
from .utils import get_default_role
from secberusAPI.settings import client
from arangodb.api import Collection, Document
from arangodb.query.simple import SimpleQuery
from django.conf import settings

from django.contrib.auth.forms import PasswordResetForm, SetPasswordForm
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_decode as uid_decoder
from django.utils.translation import ugettext_lazy as _
from django.utils.encoding import force_text

class UserSerializer(serializers.Serializer):
    first_name = serializers.CharField(max_length=30, required=True)
    last_name  = serializers.CharField(max_length=30, required=False, allow_null=True)
    email = serializers.EmailField(
                required=True,
                validators=[UniqueValidator(queryset=User.objects.all())]
            )

    password = serializers.CharField(min_length=8)
    country = serializers.CharField(max_length=30, required=True, write_only=True)
    state =  serializers.CharField(max_length=30, required=True, write_only=True)
    phone_number = serializers.CharField(max_length=30, required=True, write_only=True)
    company = serializers.CharField(required=True,
                write_only=True)


    # Custom validation for unqieu company name
    def validate_company(self, data):
        collection = Collection.get_loaded_collection(name='Companies')
        if SimpleQuery.get_by_example(collection, example_data= {'name': str(data)}):
            raise serializers.ValidationError("Company already exist")

        return data

    def create(self, validated_data):
        user = User.objects.create_user(
                    username=validated_data['email'],
                    password=validated_data['password'],
                    email=validated_data['email'],
                    first_name=validated_data['first_name'],
                    last_name=validated_data['last_name'] if 'last_name' in validated_data else '',
                    is_active=False
                )
        try:
            # Saving data into UserProfile collection
            UserProfiles.init()
            obj = UserProfiles()
            obj.user = int(user.id)
            obj.country = str(validated_data['country'])
            obj.state = str(validated_data['state'])
            obj.phone_number = str(validated_data['phone_number'])
            obj.role = str(get_default_role().id)
            obj.save()


            # Saving company into collection
            Companies.init()
            obj = Companies()
            obj.name = str(validated_data['company'])
            obj.save()

            # Assign User to Company
            collection = Collection.get_loaded_collection(name='UserCompanies')
            doc = collection.create_document()
            doc.user = int(user.id)
            doc.company =  str(obj.id)
            doc.active =  True
            doc.created_on = str(datetime.datetime.now())
            doc.save()

        except Exception as e:
            # Removing data saved into document if any error occured
            collection = Collection.get_loaded_collection(name='UserProfiles')
            obj = SimpleQuery.get_by_example(collection, example_data={
                'user': int(user.id),
            })
            if obj:
                Document(obj.id, '', 'UserProfiles', client.api).delete()

            collection = Collection.get_loaded_collection(name='Companies')
            obj = SimpleQuery.get_by_example(collection, example_data={
                'name': str(validated_data['company']),
            })
            if obj:
                Document(obj.id, '', 'Companies', client.api).delete()

            collection = Collection.get_loaded_collection(name='UserCompanies')
            obj = SimpleQuery.get_by_example(collection, example_data={
                'user': int(user.id),
                'company': str(obj.id)
            })
            if obj:
                Document(obj.id, '', 'UserCompanies', client.api).delete()
            raise Exception('Error Occured '+str(e))
        return user

class ForgetPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)

    def validate_email(self,data):
        try:
            user = User.objects.get(email = data)
        except(TypeError, ValueError, OverflowError, User.DoesNotExist):
            raise serializers.ValidationError("User doesn't exist")
        return data


class ChangePasswordSerializer(serializers.Serializer):
    uidb64 = serializers.CharField(required = True)
    token = serializers.CharField(required = True)
    new_password = serializers.CharField(min_length = 8, required = True)
    confirm_password = serializers.CharField(min_length = 8, required = True)

    def validate(self,data):
        password = data.get('new_password')
        password2 = data.get('confirm_password')
        
        if not password == password2:
            raise serializers.ValidationError('Password not matches with each other')
        return super(ChangePasswordSerializer, self).validate(data)

class ActivationResendSerializer(serializers.Serializer):
    email = serializers.EmailField(required = True)

    def validate_email(self,data):
        try:
            user = User.objects.get(email = data)
        except(User.DoesNotExist):
            raise serializers.ValidationError("User doesn't exist")
        return data

