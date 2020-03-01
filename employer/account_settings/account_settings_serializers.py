from rest_framework import serializers
from employer.employer_homepage.homepage_models import *


class GetEmailSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserAccount
        fields = ['email_id']


class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmployerProfile
        fields = ['user_account_id', 'designation_id', 'organization_id', 'permission', 'sub_user_status', 'reason', 'suspended_date', 'suspended_till', 'deleted_date']
        depth = 2
