# This file contains functions to do some specified task in Job seeker registration. 
# The functions are send otp, generate random number for otp, send and resend api function, is email valid or not and is phone valid or not.

import requests
from job_seeker.models import *
import re
from pinkjob.utils import *
import time
import jwt
import datetime
base_url = "http://35.244.0.27/pinkjob"


# this is a function use to send otp using an API
def send_OTP(country_code,otp,number):
        if country_code == "+91" or country_code == '91' or country_code == 91 or country_code == ' 91':
                payload1 = "http://enterprise.smsgupshup.com/GatewayAPI/rest?method=SendMessage&send_to=91"+str(number)+"&msg=Use "+str(otp)+" as your one time password for your mobile number verification.&msg_type=TEXT&userid=2000146610&auth_scheme=plain&password=0rDAyBGGG&v=1.1&format=text&mask=TATAVH"
                response = requests.request("GET", payload1) 
                print(response.text)
        else:
                print("Country other than India")


# This is a function to generate a random number for OTP
def get_random_number():
    return random.randint(1000,9999)


# this is function used by an api MobileOTPSend for sending otp
def OTP_send(req):
    otp = get_random_number()
    send_OTP(req["country_code"],otp,req["mobile_no"])
    data={"verification_type":"number","verification_id":req["mobile_no"],"otp":otp,"otp_status":"N","timestamp":int(time.time()*1000)}
    OTPVerification.objects.create(**data)


# this is function used by an api MobileOTPSend for resending otp
def OTP_resend(req):
    otp = get_random_number()
    send_OTP(req["country_code"],otp,req["mobile_no"])
    for resend in OTPVerification.objects.filter(verification_id=req["mobile_no"]).order_by('-id'):
        resend.otp =  otp
        resend.save()
        resend.otp_status = "N"
        resend.save()
        break
    print(otp)


# this is use to check is phone valid or not
def is_valid_phone(number):
        Pattern = re.compile("(0/91)?[7-9][0-9]{9}") 
        return Pattern.match(number) 


# After job seeker registered with us then varification email send by this function with jwt verification details
def send_verification_email(email_id):
        private_key = open('jwt-key').read()
        public_key = open('jwt-key.pub').read()
        exp = datetime.datetime.utcnow() + datetime.timedelta(minutes=60)
        payload = {"iat":datetime.datetime.utcnow(),"exp":exp,"email_id":email_id,"user_type":1}
        token = jwt.encode(payload,private_key,algorithm='RS256')
        print(token.decode("utf-8") )
        url = base_url+"/job-seeker-registration/verify-email?token="+token.decode("utf-8") 
        body = "Hi '"+email_id+"',<br><br>Thank you for signing up with Shenzyn.<br><br>To complete the setup, click <a href='"+url+"'>here</a> to verify your email address.<br><br>After you're verified, you can sign in to your 'Shenzyn' Account at 'https://jobportal.com/name'. Please bookmark this URL now.<br><br>If you have questions, contact our Customer Service team.<br><br>Your Shynzyn team"
        subject = "Verify Email with shenzyn"
        send_email(subject,body,"gupta@selekt.in",[email_id])


def update_new_values_job_seeker(table_name, value, field_name):
    if type(value) is int:
        return value
    search_type = '__icontains'
    field_nm = field_name + search_type
    info = table_name.objects.filter(**{field_nm: value})
    if info:
        return info[0].id
    else:
        new_value = table_name.objects.create(**{field_name:value})
        return new_value.id
