from employer.models import *
from job_seeker.models import Location, Designation
from partial_date import PartialDateField
import time
from datetime import datetime


class Organizations(models.Model):
    name = models.CharField(max_length=255)
    is_default = models.BooleanField(default=0)


class Industries(models.Model):
    name = models.CharField(max_length=255)
    is_default = models.BooleanField(default=0)


class FunctionalAreas(models.Model):
    name = models.CharField(max_length=255)
    is_default = models.BooleanField(default=0)


class LevelIHire(models.Model):
    name = models.CharField(max_length=255)
    is_default = models.BooleanField(default=0)


class CompanyDetails(models.Model):
    pan = models.CharField(max_length=10,null=True)
    pan_file_path = models.FileField(upload_to='documnets/%Y/%m/%D/',null=True,blank=True)
    other_file_path = models.FileField(upload_to='documnets/%Y/%m/%D/',null=True,blank=True)
    is_company_verified = models.BooleanField(default=0)


class EmployerProfile(models.Model):
    user_account_id = models.OneToOneField(UserAccount, related_name='user_account_id_profile', on_delete=models.CASCADE)
    designation_id = models.ForeignKey(Designation, related_name='designation_id', on_delete=models.CASCADE, null=True)
    organization_id = models.ForeignKey(Organizations, related_name='organizations_id', on_delete=models.CASCADE,null=True)
    facebook_url = models.CharField(max_length=255,null=True)
    linkedin_url = models.CharField(max_length=255,null=True)
    current_country = models.ForeignKey(Location, related_name='current_country_id', on_delete=models.CASCADE, null=True)
    current_city = models.ForeignKey(Location, related_name='current_city_id', on_delete=models.CASCADE, null=True)
    business_email = models.EmailField(max_length=329, null=True)
    is_business_email_verified = models.BooleanField(default=0)
    secondary_email = models.EmailField(max_length=329,null=True)
    profile_headline = models.CharField(max_length=300,null=True)
    parent_id = models.ForeignKey(UserAccount, related_name='parent_id', on_delete=models.CASCADE,null=True)
    permissions = models.TextField(null=True)
    is_admin = models.BooleanField(default=0)
    suspended_date = models.BigIntegerField(null=True)
    suspended_till = models.DateField(null=True)
    customize_profile_url = models.CharField(max_length=30,null=True)
    about_employer = models.CharField(max_length=30,null=True)
    employer_profile_status = models.CharField(max_length=30,null=True)
    created_on = models.BigIntegerField(null=True)
    updated_on = models.BigIntegerField(null=True)
    reason = models.CharField(max_length=500, null=True)
    company_details_id = models.ForeignKey(CompanyDetails, related_name='employer_company_details_id', on_delete=models.CASCADE, null=True)


class EmployerWorkExperience(models.Model):
    user_account_id = models.ForeignKey(UserAccount, related_name='user_account_id_work_experience', on_delete=models.CASCADE)
    designation_id = models.ForeignKey(Designation, related_name='designation_id1', on_delete=models.CASCADE,null=True)
    organization_id = models.ForeignKey(Organizations, related_name='organizations_id1', on_delete=models.CASCADE,null=True)
    description = models.CharField(max_length=500,null=True)
    is_current_job = models.BooleanField(default=True)
    start_date = PartialDateField(null=True)
    end_date = PartialDateField(null=True)


class EmployerDocuments(models.Model):
    user_account_id = models.ForeignKey(UserAccount, related_name='user_account_id_documents', on_delete=models.CASCADE)
    document = models.FileField(upload_to='documnets/%Y/%m/%D/',null=True,blank=True)
    document_name = models.CharField(max_length=50, null=True)


class DefaultPermissions(models.Model):
    permission_name = models.CharField(max_length=50, null=True)
    is_admin = models.BooleanField(default=True)
