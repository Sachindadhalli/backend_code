from .homepage_models import *
from rest_framework import serializers


class EmployerWorkExperienceSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmployerWorkExperience
        fields = '__all__'

class EmployerProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmployerProfile
        fields = '__all__'


class IndustriesSerializer(serializers.ModelSerializer):
    value = serializers.CharField(source='name')
    key = serializers.IntegerField(source='id')

    class Meta:
        model = Industries
        fields = ('key', 'value')


class FunctionalAreasSerializer(serializers.ModelSerializer):
    value = serializers.CharField(source='name')
    key = serializers.IntegerField(source='id')

    class Meta:
        model = FunctionalAreas
        fields = ('key', 'value')


class LevelIHireSerializer(serializers.ModelSerializer):
    value = serializers.CharField(source='name')
    key = serializers.IntegerField(source='id')

    class Meta:
        model = LevelIHire
        fields = ('key', 'value')


# This serialiser used for only geting company document urls
class EmployerDocumentsSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmployerProfile
        fields = ["company_details_id"]
        depth = 2


# This seriliser used in get basic profile deatils
class EmployerBasicProfileDetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmployerProfile
        fields = ("current_city","current_country","organization_id","designation_id","user_account_id")
        depth = 2


class OrganizationsSerializer(serializers.ModelSerializer):
    value = serializers.CharField(source='name')
    key = serializers.IntegerField(source='id')

    class Meta:
        model = Organizations
        fields = ('key', 'value')


class DefaultPermissionsSerializer(serializers.ModelSerializer):
    class Meta:
        model = DefaultPermissions
        fields = ["permission_name"]
