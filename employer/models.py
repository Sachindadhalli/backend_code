from django.db import models


class Employer(models.Model):
    name = models.CharField(max_length=255)
    email = models.EmailField(max_length=255)
    mobile_number = models.BigIntegerField()
    created_on = models.DateTimeField(auto_now_add=True)


class UserAccount(models.Model):
    id = models.AutoField(primary_key=True)
    first_name = models.CharField(max_length=30,null=True)
    middle_name = models.CharField(max_length=30,null=True)
    last_name = models.CharField(max_length=20,null=True)
    email_id = models.EmailField(max_length=320)
    country_code = models.IntegerField(default=91)
    mobile_number = models.CharField(max_length=15,null=True)
    dob = models.DateField(null=True)
    password = models.CharField(max_length=200)
    regestration_date = models.BigIntegerField(null=True)
    profile_image_path = models.FileField(upload_to='profile/%Y/%m/%D/',null=True,blank=True)
    address = models.CharField(max_length=255,null=True)
    pincode = models.IntegerField(null=True)
    is_employer = models.BooleanField(default=0)
    is_job_seeker = models.BooleanField(default=0)
    is_sms_notification_active = models.BooleanField(default=0)
    is_email_notification_active = models.BooleanField(default=0)
    is_account_approved = models.BooleanField(default=0)
    is_email_verified = models.BooleanField(default=0)


class UserLinkedinDetails(models.Model):
    user_account_id = models.OneToOneField(UserAccount, related_name='user_account_id_linkedin', on_delete=models.CASCADE)
    access_token = models.CharField(max_length=1000,null=True)
    refresh_token = models.CharField(max_length=1000,null=True)
    profile_pic_url = models.CharField(max_length =1000,null=True)


class UserGmailLoginDetails(models.Model):
    user_account_id = models.ForeignKey(UserAccount, related_name='user_account_id_gmail', on_delete=models.CASCADE)
    access_token = models.CharField(max_length=1000,null=True)
    refresh_token = models.CharField(max_length=1000,null=True)
    profile_pic_url = models.CharField(max_length =1000,null=True)

