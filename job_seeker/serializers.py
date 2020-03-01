# This is a serializer file which contents model serializer of .model file to get database data in json format.
from .models import *
from rest_framework import serializers
from employer.models import UserAccount

# folowing are the seriralizers for database output objects
# model assign name is database name and filed asign will whatever filed want to filter from data object


class JobSeekerSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserAccount
        fields = '__all__'


class OTPVerificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = OTPVerification
        fields = '__all__'



class AadharCardDeatilsSerialiser(serializers.ModelSerializer):
    class Meta:
        model = AadharCardDeatils
        fields = "__all__"


class EducationalQualificationsSerializer(serializers.ModelSerializer):
    value = serializers.CharField(source='qualification_name')
    key = serializers.IntegerField(source='id')

    class Meta:
        model = EducationalQualifications
        fields = ["key", "value"]


class QualificationsSerializer(serializers.ModelSerializer):
    class Meta:
        model = EducationalQualifications
        fields = ["qualification_name"]


class MajorsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Majors
        fields = ["id", "major_name"]


class MajorsKeyValueSerializer(serializers.ModelSerializer):
    value = serializers.CharField(source='major_name')
    key = serializers.IntegerField(source='id')

    class Meta:
        model = Majors
        fields = ('key', 'value')


class SpecializationsKeyValueSerializer(serializers.ModelSerializer):
    value = serializers.CharField(source='specialization_name')
    key = serializers.IntegerField(source='id')

    class Meta:
        model = Majors
        fields = ('key', 'value', "majors_id")


class SpecializationsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Specializations
        fields = ["specialization_name","id"]


class UniversitySerializer(serializers.ModelSerializer):
    value = serializers.CharField(source='university_name')
    key = serializers.IntegerField(source='id')

    class Meta:
       model = Universities
       fields = ('key', 'value')


class InstitutesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Institutes
        fields = ["institute_name"]


class BoardSerializer(serializers.ModelSerializer):
    class Meta:
        model = Boards
        fields = ["board_name","id"]


class MediumSerializer(serializers.ModelSerializer):
    class Meta:
        model = Medium
        fields = ["medium_name","id"]


class UIMappingSerializer(serializers.ModelSerializer):
    institute_id = InstitutesSerializer()

    class Meta:
        model = UniversitiesInstitutesMapping
        fields = ['institute_id',"id"]


class DesignationSerializer(serializers.ModelSerializer):
    value = serializers.CharField(source='name')
    key = serializers.IntegerField(source='id')

    class Meta:
        model = Designation
        fields = ["key", "value"]


class CompanyNamesSerializer(serializers.ModelSerializer):
    value = serializers.CharField(source='company_name')
    key = serializers.IntegerField(source='id')

    class Meta:
        model = CompanyNames
        fields = ["key", "value"]


class LocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Location
        fields = ["country"]


class SearchLocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Location
        fields = "__all__"


class CountrySerializer(serializers.ModelSerializer):
    value = serializers.CharField(source='country')
    key = serializers.IntegerField(source='id__min')

    class Meta:
        model = Location
        fields = ('value', 'key')


class StateSerializer(serializers.ModelSerializer):
    value = serializers.CharField(source='state')
    key = serializers.IntegerField(source='id__min')

    class Meta:
        model = Location
        fields = ["key", "value"]


class CitySerializer(serializers.ModelSerializer):
    value = serializers.CharField(source='city')
    key = serializers.IntegerField(source='id__min')

    class Meta:
        model = Location
        fields = ["key", "value"]


class UserAccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserAccount
        fields = ["id"]


class SkillSetSerializer(serializers.ModelSerializer):
    value = serializers.CharField(source='skill_set_name')
    key = serializers.IntegerField(source='id')

    class Meta:
        model = SkillSet
        fields = ["key", "value"]


class GradingSystemSerializer(serializers.ModelSerializer):
    value = serializers.CharField(source='grading_system_name')
    key = serializers.IntegerField(source='id')

    class Meta:
        model = GradingSystem
        fields = ["key", "value"]