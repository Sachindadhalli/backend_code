# This is model file used for creating tables in database.
# So followings functions are tables names and inside declarations are filed names in datbase.
from django.db import models
from django_mysql.models import JSONField, Model
from employer.models import *


# following all are a database table names and there filed with datatype
class JobSeeker(models.Model):
    name = models.CharField(max_length=255)
    email = models.EmailField(max_length=255)
    mobile_number = models.BigIntegerField()
    created_on = models.DateTimeField(auto_now_add=True)


class OTPVerification(models.Model):
    verification_type=models.TextField()
    verification_id=models.CharField(max_length=320)
    otp = models.IntegerField()
    otp_status =models.CharField(max_length=1)
    timestamp = models.CharField(max_length=13)


class EducationalQualifications(models.Model):
    qualification_name = models.CharField(max_length=255, blank=True)


class Majors(models.Model):
    major_name = models.TextField(blank=True)
    qualification_id = models.ForeignKey(EducationalQualifications, related_name='majors', on_delete=models.CASCADE)


class Specializations(models.Model):
    specialization_name = models.TextField(blank=True)
    majors_id = models.ForeignKey(Majors, related_name='majors', on_delete=models.CASCADE)


class Universities(models.Model):
    university_name = models.TextField(blank=True)


class Institutes(models.Model):
    institute_name = models.TextField(blank=True)


class UniversitiesInstitutesMapping(models.Model):
    university_id = models.ForeignKey(Universities, related_name='university', on_delete=models.CASCADE)
    institute_id = models.ForeignKey(Institutes, related_name='institute', on_delete=models.CASCADE)


class Boards(models.Model):
    board_name = models.TextField(blank=True)


class Medium(models.Model):
    medium_name = models.TextField(blank=True)


class Designation(models.Model):
    name = models.CharField(max_length=255)
    is_default = models.BooleanField(default=0)


class CompanyNames(models.Model):
    company_name = models.TextField(blank=True)


class Location(models.Model):
    country = models.CharField(max_length=200)
    state = models.CharField(max_length=200)
    city = models.CharField(max_length=200)


class GradingSystem(models.Model):
    grading_system_name = models.CharField(max_length=10,null=True)

    
class SeekerProfile(Model):
    user_account_id = models.OneToOneField(UserAccount, related_name='user_account_seeker_id', on_delete=models.CASCADE)
    current_salary = models.IntegerField(null=True)
    is_annually_monthly = models.BooleanField(default=0)
    is_fresher = models.BooleanField(default=0)
    currency = models.CharField(max_length=50,null=True)
    resume_document1 = models.FileField(upload_to='documents/%Y/%m/%D/',null=True,blank=True)
    resume_video1 = models.FileField(upload_to='video/%Y/%m/%D/',null=True,blank=True)
    resume_document2 = models.FileField(upload_to='documents/%Y/%m/%D/',null=True,blank=True)
    resume_video2 = models.FileField(upload_to='video/%Y/%m/%D/',null=True,blank=True)
    notice_period = models.CharField(max_length=20,null=True)
    break_reason = models.CharField(max_length=50,null=True)
    break_duration = models.CharField(max_length=50,null=True)
    address = models.CharField(max_length=1000,null=True)
    pincode = models.IntegerField(null=True)
    martial_status= models.CharField(max_length=20,null=True)
    differently_abled= JSONField(default='{}')
    work_permit_usa= models.CharField(max_length=40,null=True)
    work_permit_other= models.CharField(max_length=100,null=True)
    desired_career_profile= JSONField(default='{}')
    #aadhar_path= models.ImageField(upload_to='aadhar/%Y/%m/%D/', null=True, blank=True)
    aadhar_url = models.CharField(max_length=400, null=True)
    resume_headline = models.CharField(max_length=300, null=True)
    photo_path = models.FileField(upload_to='photo/%Y/%m/%D/',null=True,blank=True)
    skill_name = models.CharField(max_length=300,null=True)
    technologies = models.CharField(max_length=40, null=True)
    profile_summery = models.CharField(max_length=1000, null=True)
    project_title = models.CharField(max_length=50, null=True)
    role = JSONField(default='{}')
    client = JSONField(default='{}')
    details_of_project = models.CharField(max_length=1000, null=True)
    #team_size = models.JSONField()
    role_description = models.CharField(max_length=250, null=True)



class AadharCardDeatils(models.Model):
    path = models.FileField(upload_to='aadhar/%Y/%m/%D/', null=True, blank=True)


class ExperienceDetails(models.Model):
    user_account_id = models.ForeignKey(UserAccount, related_name='user_account_exp_id', on_delete=models.CASCADE)
    is_current_job = models.BooleanField(default=0)
    start_date = models.DateField(null=True)
    end_date = models.DateField(null=True)
    job_title = models.ForeignKey(Designation, related_name='designation', on_delete=models.CASCADE,null=True)
    company_name = models.ForeignKey(CompanyNames, related_name='companies', on_delete=models.CASCADE,null=True)
    city = models.ForeignKey(Location, related_name='id_city', on_delete=models.CASCADE,null=True)
    state = models.ForeignKey(Location, related_name='id_state', on_delete=models.CASCADE,null=True)
    country = models.ForeignKey(Location, related_name='id_country', on_delete=models.CASCADE,null=True)
    description = models.TextField(null=True)
    annual_salary = models.BigIntegerField(null=True)


class EducationalDetails(models.Model):
    user_account_id = models.ForeignKey(UserAccount, related_name='user_account_edu_id', on_delete=models.CASCADE)
    degree_name = models.ForeignKey(EducationalQualifications, related_name='degree', on_delete=models.CASCADE,null=True)
    major = models.ForeignKey(Majors, related_name='major', on_delete=models.CASCADE,null=True)
    specialization = models.ForeignKey(Specializations, related_name='specialization', on_delete=models.CASCADE,null=True)
    university = models.ForeignKey(Universities, related_name='universities', on_delete=models.CASCADE,null=True)
    institute = models.ForeignKey(Institutes, related_name='insitute', on_delete=models.CASCADE,null=True)
    start_date = models.DateTimeField(null=True)
    completion_date = models.DateTimeField(null=True)
    grading_system = models.ForeignKey(GradingSystem, related_name='grading_system_edu_id', on_delete=models.CASCADE,null=True)
    percentage = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    board = models.ForeignKey(Boards, related_name='board', on_delete=models.CASCADE,null=True)
    medium = models.ForeignKey(Medium, related_name='mediums', on_delete=models.CASCADE,null=True)
    passed_out_year = models.CharField(max_length=10,null=True)


class SkillSet(models.Model):
    skill_set_name = models.CharField(max_length=50,null=True)


class SeekerSkillSet(models.Model):
    user_account_id = models.ForeignKey(UserAccount, related_name='user_account_skill_id', on_delete=models.CASCADE)
    skill_set_id = models.ForeignKey(SkillSet, related_name='skill_set_name_id', on_delete=models.CASCADE)


