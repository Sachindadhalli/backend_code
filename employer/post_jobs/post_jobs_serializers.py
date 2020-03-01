from rest_framework import serializers
from .post_jobs_models import *
from job_seeker.serializers import SearchLocationSerializer, SkillSetSerializer, MajorsSerializer, SpecializationsSerializer
from employer.employer_homepage.homepage_serializers import OrganizationsSerializer


# folLowing seriralizers are used for json readable object from database queryset
# model assign name is database name and fileds assign is whatever filed want to filter from data object
# In serializer class calling aother class is know as nested serializer for geting related data from another tables


class SearchDesireCandidateProfileSkillsSerializer(serializers.ModelSerializer):
    qualities = SkillSetSerializer()
    class Meta:
        model = DesireCandidateProfileSkills
        fields = '__all__'


class SearchWorkingHoursSerializer(serializers.ModelSerializer):
    class Meta:
        model = WorkingHours
        fields = '__all__'


class SearchJobLocationsSerialiser(serializers.ModelSerializer):
    country_id = SearchLocationSerializer()
    city_id = SearchLocationSerializer()
    class Meta:
        model = JobLocations
        fields = '__all__'


class SearchWalkinDetailsSerialiser(serializers.ModelSerializer):
    class Meta:
        model = WalkinDetails
        fields = "__all__"


class SearchJobPostQuestionnaireSerialiser(serializers.ModelSerializer):
    class Meta:
        model = JobPostQuestionnaire
        fields = "__all__"


class SearchJobRequiredQualificationsSerializer(serializers.ModelSerializer):
    major_id = MajorsSerializer()
    specialization_id = SpecializationsSerializer()

    class Meta:
        model = JobRequiredQualifications
        fields = "__all__"


class SearchPHDJobRequiredQualificationsSerializer(serializers.ModelSerializer):
    phd_major_id = MajorsSerializer()
    phd_specialization_id = SpecializationsSerializer()

    class Meta:
        model = JobRequiredPHDQualifications
        fields = "__all__"


class SearchShowOrHideOrganisationsSerialiser(serializers.ModelSerializer):
    organisation_id = OrganizationsSerializer()
    class Meta:
        model = ShowOrHideOrganisations
        fields = "__all__"


class SearchAdvertiseCompanyDetailsJobMappingSerialiser(serializers.ModelSerializer):
    class Meta:
        model = AdvertiseCompanyDetailsJobMapping
        fields = "__all__"
        depth = 2


class SearchPostJobsSerializer_1(serializers.ModelSerializer):
    job_id_skill = SearchDesireCandidateProfileSkillsSerializer(many=True)
    job_id_time = SearchWorkingHoursSerializer(many=True)
    job_id_location = SearchJobLocationsSerialiser(many=True)
    job_id_walkin = SearchWalkinDetailsSerialiser(many=True)
    job_id_post_questionnaire = SearchJobPostQuestionnaireSerialiser(many=True)
    job_id_qualification1 = SearchJobRequiredQualificationsSerializer(many=True)
    job_id_qualification2 = SearchPHDJobRequiredQualificationsSerializer(many=True)
    job_id_hide_or_show = SearchShowOrHideOrganisationsSerialiser(many=True)
    post_jobs_advertise_id = SearchAdvertiseCompanyDetailsJobMappingSerialiser(many=True)

    class Meta:
        model = PostJobs
        fields = "__all__"


class SearchPostJobsSerializer(serializers.ModelSerializer):
    class Meta:
        model = PostJobs
        fields = ("id", "job_title", "created_on")


class ExistingEmailSerializer(serializers.ModelSerializer):
    class Meta:
        model = PostJobs
        fields = ["forward_email_id"]


class AdvertiseSerializer(serializers.ModelSerializer):
    description = serializers.CharField(source='organisation_description')
    url = serializers.CharField(source='website_url')
    number = serializers.CharField(source='contact_number')
    file_url = serializers.FileField(source='file_path')
    key = serializers.IntegerField(source='id')
    class Meta:
        model = AdvertiseCompanyDetails
        fields = ("key", "description", "url", "address", "number", "file_url", "organisation_name", "contact_person")


class AdvertiseCompanyDetailsUserMappingSerialiser(serializers.ModelSerializer):
    class Meta:
        model = AdvertiseCompanyDetailsUserMapping
        fields = "__all__"
        depth = 2


class EmployerQuestionnaireSerialiser(serializers.ModelSerializer):
    class Meta:
        model = EmployerQuestionnaire
        fields = ("id","questionnaire_id")
        depth = 2


class QuestionOptionsMappingSerialiser(serializers.ModelSerializer):
    class Meta:
        model = QuestionOptionsMapping
        fields = "__all__"
        depth = 2

class QuestionnaireQuestionsSerialiser(serializers.ModelSerializer):
    class Meta:
        model = QuestionnaireQuestions
        fields = "__all__"
        depth = 2


class QuestionnaireSerialiser(serializers.ModelSerializer):
    questionnaire_id_questions = QuestionnaireQuestionsSerialiser(many=True)

    class Meta:
        model = Questionnaire
        fields = "__all__"
