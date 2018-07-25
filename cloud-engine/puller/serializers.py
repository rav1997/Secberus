from rest_framework import serializers
from django.contrib.auth.models import User
from aws.models import AwsCredentials
from company.models import Companies

class PullerSerializer(serializers.Serializer):
    account_id = serializers.CharField(required=True)
    service = serializers.ChoiceField(choices=[
            ('assets', 'For assets'),
            ('iam', 'For iam policy'),
            ('lambda', 'For Lambda functions'),
            ('rds', 'For rds'),
            ('s3', 'For s3 bucket'),
            ('cloud-trail', 'For cloud trail'),
            ('cloud-watch', 'For cloud watch'),
            ('vpc', 'For VPC'),
            ('all', 'For all aws services')
        ], allow_blank=False, write_only=True)

    # Custom validation to check a setting document exist.
    def validate(self, data):
        AwsCredentials.init()
        Companies.init()
        aws_obj = AwsCredentials.objects.get(_id=str(data['account_id']))
        if str(aws_obj.company.id) != str(self.context['company']):
            raise serializers.ValidationError('Companies account are different for Aws and currenly logged in User')

        return data
