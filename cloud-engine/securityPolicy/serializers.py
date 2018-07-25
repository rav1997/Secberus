from __future__ import unicode_literals
from rest_framework import serializers

class ListPolicySerializer(serializers.Serializer):
    account_id = serializers.CharField(required=True)

class PolicyRuleSerializer(serializers.Serializer):
    security_policy_id = serializers.CharField(required=True)
