from django.db import models
from django_mysql.models import EnumField
from employer.employer_homepage.homepage_models import FunctionalAreas, Industries, Organizations
from employer.models import UserAccount
from job_seeker.models import Designation, Location, Majors, Specializations, SkillSet

class Currency(models.Model):
    name = models.CharField(max_length=100, null=True)
    code = models.CharField(max_length=3, null=True)
    symbol = models.CharField(max_length=5, null=True)


class PostJobs(models.Model):
    user_account_id = models.ForeignKey(UserAccount, related_name='user_account_id_post', on_delete=models.CASCADE,
                                        null=True)
    job_title = models.CharField(max_length=1000, null=True)
    job_role = models.ForeignKey(Designation, related_name='designations_id_post', on_delete=models.CASCADE, null=True)
    job_description = models.CharField(max_length=900, null=True)
    min_experience = models.IntegerField(null=True)
    max_experience = models.IntegerField(null=True)
    is_fresher = models.BooleanField(default=0)
    currency = models.ForeignKey(Currency, related_name='currency_job_post', on_delete=models.CASCADE, null=True)
    min_salary = models.CharField(max_length=45, null=True)
    max_salary = models.CharField(max_length=45, null=True)
    is_salary_visible = models.BooleanField(default=0)
    no_of_vacancies = models.IntegerField(null=True)
    how_soon_required = models.CharField(max_length=100, null=True)
    industries_id = models.ForeignKey(Industries, related_name='industry_id_post', on_delete=models.CASCADE, null=True)
    functional_area_id = models.ForeignKey(FunctionalAreas, related_name='functional_area_id_post', on_delete=models.CASCADE, null=True)
    type_of_job = EnumField(choices=["Part time", "Full time", "Part-time work from home", "Full-time work from home", "Freelancer"], null=True)
    is_longtime_break = models.BooleanField(default=0)
    reference_code = models.CharField(max_length=10, null=True)
    is_email_response = models.BooleanField(default=1)
    is_email_forward = models.BooleanField(default=0)
    forward_email_id = models.CharField(max_length=320, null=True)
    schedule_time = EnumField(choices=["Week", "Fortnight", "Month"], null=True)
    status = EnumField(choices=["Post", "Draft", "Save"], null=True)
    hire_for = models.CharField(max_length=45, null=True)
    from_count = models.IntegerField(null=True)
    is_phd_premium_university = models.BooleanField(default=0)
    is_graduate_premium_university = models.BooleanField(default=0)
    candidate_profile = models.TextField(null=True)
    created_on = models.DateTimeField(auto_now_add=True)


class WorkingHours(models.Model):
    job_id = models.ForeignKey(PostJobs, related_name="job_id_time", on_delete=models.CASCADE, null=True)
    time_type = models.CharField(max_length=45, null=True)
    start_time = models.CharField(max_length=50, null=True)
    end_time = models.CharField(max_length=50, null=True)


class JobRequiredQualifications(models.Model):
    major_id = models.ForeignKey(Majors, related_name="major_id_qualification1", on_delete=models.CASCADE, null=True)
    specialization_id = models.ForeignKey(Specializations, related_name="specialization_id_qualification1", on_delete=models.CASCADE, null=True)
    job_id = models.ForeignKey(PostJobs, related_name="job_id_qualification1", on_delete=models.CASCADE, null=True)


class JobRequiredPHDQualifications(models.Model):
    phd_major_id = models.ForeignKey(Majors, related_name="major_id_qualification2", on_delete=models.CASCADE, null=True)
    phd_specialization_id = models.ForeignKey(Specializations, related_name="specialization_id_qualification2", on_delete=models.CASCADE, null=True)
    job_id = models.ForeignKey(PostJobs, related_name="job_id_qualification2", on_delete=models.CASCADE, null=True)


class DesireCandidateProfileSkills(models.Model):
    job_id = models.ForeignKey(PostJobs, related_name="job_id_skill", on_delete=models.CASCADE, null=True)
    qualities = models.ForeignKey(SkillSet, related_name="job_id_skillset", on_delete=models.CASCADE, null=True)


class JobLocations(models.Model):
    job_id = models.ForeignKey(PostJobs, related_name="job_id_location", on_delete=models.CASCADE, null=True)
    country_id = models.ForeignKey(Location, related_name="job_id_country", on_delete=models.CASCADE, null=True)
    city_id = models.ForeignKey(Location, related_name='job_id_city', on_delete=models.CASCADE, null=True)


class WalkinDetails(models.Model):
    job_id = models.ForeignKey(PostJobs, related_name="job_id_walkin", on_delete=models.CASCADE, null=True)
    start_date = models.DateField(null=True)
    end_date = models.DateField(null=True)
    start_time = models.TimeField(null=True)
    end_time = models.TimeField(null=True)
    venue = models.TextField(null=True)
    location_url = models.TextField(null=True)


class Questionnaire(models.Model):
    questionnaire_name = models.CharField(max_length=255, null=True)


class Questions(models.Model):
    question_text = models.CharField(max_length=100, null=True)
    is_mandatory = models.BooleanField(default=0)


class InputType(models.Model):
    input_type = models.CharField(max_length=100, null=True)


class OptionValues(models.Model):
    option_name = models.CharField(max_length=45, null=True)


class QuestionOptionsMapping(models.Model):
    input_type_id = models.ForeignKey(InputType, related_name="input_type_id", on_delete=models.CASCADE, null=True)
    question_id = models.ForeignKey(Questions, related_name="question_id1", on_delete=models.CASCADE, null=True)
    option_values_id = models.ForeignKey(OptionValues, related_name="options_value_id", on_delete=models.CASCADE, null=True)


class JobPostQuestionnaire(models.Model):
    job_id = models.ForeignKey(PostJobs, related_name="job_id_post_questionnaire", on_delete=models.CASCADE, null=True)
    questionnaire_id = models.ForeignKey(Questionnaire, related_name="questionnaire_id", on_delete=models.CASCADE, null=True)
    user_id = models.ForeignKey(UserAccount, related_name="user_id", on_delete=models.CASCADE, null=True)


class EmployerQuestionnaire(models.Model):
    questionnaire_id = models.ForeignKey(Questionnaire, related_name="questionnaire_id2", on_delete=models.CASCADE, null=True)
    user_id = models.ForeignKey(UserAccount, related_name="user_id2", on_delete=models.CASCADE, null=True)


class QuestionnaireQuestions(models.Model):
    questionnaire_id = models.ForeignKey(Questionnaire, related_name="questionnaire_id_questions", on_delete=models.CASCADE, null=True)
    question_id = models.ForeignKey(Questions, related_name="questionnaire_id", on_delete=models.CASCADE, null=True)


class AdvertiseCompanyDetails(models.Model):
    organisation_name = models.ForeignKey(Organizations, related_name="organisation_id_advertise", on_delete=models.CASCADE, null=True)
    organisation_description = models.CharField(max_length=300, null=True)
    website_url = models.TextField(null=True)
    address = models.CharField(max_length=250, null=True)
    contact_number = models.CharField(max_length=15, null=True)
    contact_person = models.CharField(max_length=255,null=True)
    file_path = models.FileField(upload_to='company_details/%Y/%m/%D/', null=True, blank=True)


class AdvertiseCompanyDetailsJobMapping(models.Model):
    advertise_company_details_id = models.ForeignKey(AdvertiseCompanyDetails, related_name="advertise_company_details_job_map", on_delete=models.CASCADE, null=True)
    job_id = models.ForeignKey(PostJobs, related_name="post_jobs_advertise_id", on_delete=models.CASCADE, null=True)


class AdvertiseCompanyDetailsUserMapping(models.Model):
    advertise_company_details_id = models.ForeignKey(AdvertiseCompanyDetails, related_name="advertise_company_details_user_map", on_delete=models.CASCADE, null=True)
    user_account_id = models.ForeignKey(UserAccount, related_name="user_account_advertise_id", on_delete=models.CASCADE, null=True)


class EmployerIndustriesMapping(models.Model):
    user_account_id = models.ForeignKey(UserAccount, related_name="user_account_employer_industries_mapping_id", on_delete=models.CASCADE, null=True)
    industries_id = models.ForeignKey(Industries, related_name="industries_employer_industries_mapping_id", on_delete=models.CASCADE, null=True)


class ShowOrHideOrganisations(models.Model):
    job_id = models.ForeignKey(PostJobs, related_name="job_id_hide_or_show", on_delete=models.CASCADE, null=True)
    organisation_id = models.ForeignKey(Organizations, related_name="organisation_id_show_or_hide", on_delete=models.CASCADE, null=True)
    is_show = models.BooleanField(default=0)
