# This file contains login page API's for Job seeker login. 
#The apis are login, forgot password, change password, otp validation. 

from rest_framework.views import APIView
from rest_framework.response import Response
from job_seeker.serializers import *
from job_seeker.models import *
from pinkjob.utils import *
from employer.models import *
import datetime
import time
import jwt
private_key = open('jwt-key').read()
public_key = open('jwt-key.pub').read()


#This function will check email id is exists in database or not
#It will take email_id and extra one parameter(is_employer or is_job_seeker)
def check_job_seeker_email_in_database(email_id):
    query = UserAccount.objects.filter(email_id=email_id,is_job_seeker=1)
    serializer = JobSeekerSerializer(query, many=True).data
    if serializer:
        return False
    else:
        return True    

#This function is used for login with email_id & password or token
#In this function we will check email_id and password are correct or not
#If it is correct we will send access token and refresh token
#same with refresh token 
class Login(APIView):
    def post(self, request):
        data = request.data
        if (('email_id' and 'password') or 'refresh_token') in data.keys():
            if 'password' in data.keys():
                validate_form = validate_login_form(data)
                if validate_form['status']:
                    query = UserAccount.objects.filter(email_id=data['email_id'],password=data['password'],is_job_seeker=1)
                    serializer = JobSeekerSerializer(query, many=True).data
                    if serializer:
                        if serializer[0]["is_email_verified"]:
                            remember = data["remember"]
                            exp = 0 if remember==1 else datetime.datetime.utcnow() + datetime.timedelta(minutes=60)
                            payload = {"iat":datetime.datetime.utcnow(),"exp":exp,"user_id":serializer[0]['id'],"user_type":3} #0 for admin 1 for employer 3 for job seeker
                            access_token = jwt.encode(payload,private_key,algorithm='RS256')
                            exp = 0 if remember==1 else datetime.datetime.utcnow() + datetime.timedelta(minutes=120)
                            payload = {"iat":datetime.datetime.utcnow(),"exp":exp,"user_id":serializer[0]['id'],"user_type":3}
                            refresh_token = jwt.encode(payload,private_key,algorithm='RS256')
                            return Response({"status": True, "message": Message["JOB_SEEKER_LOGIN"]["LOGIN_SUCCESS"],"data": {"access_token": access_token, "refresh_token": refresh_token,}}, status=200)
                        else:
                            return Response({"status": False, "message":Message["JOB_SEEKER_LOGIN"]["LOGIN_EMAIL_ID_NOT_VERIFIED"]}, status=200)   
                    else:
                        return Response({"status": False, "message":Message["JOB_SEEKER_LOGIN"]["LOGIN_EMAIL_ID_PASSWORD_WRONG"]}, status=200)
                else:
                    return Response({"status": False, "message":validate_form['reason']}, status=200)
            else:
                try:
                    refresh = data["refresh_token"]
                    payload = jwt.decode(refresh, public_key, algorithms=['RS256'])
                    payload["iat"] = datetime.datetime.utcnow()
                    payload["exp"] = datetime.datetime.utcnow() + datetime.timedelta(minutes=60);
                    access_token = jwt.encode(payload, private_key, algorithm='RS256')
                    payload["iat"] = datetime.datetime.utcnow()
                    payload["exp"] = datetime.datetime.utcnow() + datetime.timedelta(minutes=120);
                    refresh_token = jwt.encode(payload, private_key, algorithm='RS256')
                    return Response({"status": True, "message": Message["JOB_SEEKER_LOGIN"]["LOGIN_SUCCESS"],"data": {"access_token": access_token, "refresh_token": refresh_token,}}, status=200)
                except Exception as e:
                    print(e)
                    return Response({"status": False, "message":Message["JOB_SEEKER_LOGIN"]["LOGIN_REFRESH_TOKEN_EXPIRED"]}, status=200)
        else:
            return Response({"status": False, "message":Message["JOB_SEEKER_LOGIN"]["LOGIN_FIELDS_MISSING"]}, status=200)



class FBLogin(APIView):
    def get(self,request):
        return Response({"status": False, "message":"Error"}, status=200)

class GmailLogin(APIView):
    def get(self, request):
        return Response({"status": False, "message":"Error"}, status=200)

#This function is used for send email otp to requested user for forgot password
#It will check email id is registed with us as  job seeker or not
#If it is registred it will sent otp to user mail
#Other wise it will return false with message
class ForgotPassword(APIView):
    def get(self, request):
        if 'email_id' in request.GET:
            try:
                if not check_job_seeker_email_in_database(request.GET["email_id"]):
                    otp = get_random_number()
                    otp = str(otp)
                    print("---------------")
                    data={"verification_type":"email_id","verification_id":request.GET["email_id"],"otp":otp,"otp_status":"N","timestamp":int(time.time()*1000)}
                    OTPVerification.objects.create(**data)
                    subject = "OTP verification"
                    body = "Dear "+request.GET["email_id"]+",<br><br>Please enter below OTP to reset your Shenzyn account password.<br><br>"+otp+"<br>Note: This OTP is valid for the next 2 hours only<br>Regards,<br>Shenzyn"
                    send_email(subject,body,"gupta@selekt.in",[request.GET["email_id"]])
                    return Response({"status":True, "message":Message["JOB_SEEKER_LOGIN"]["OTP_SENT_TO_EMAIL"]},status=200) 
                else:
                    return Response({"status":False, "message":Message["JOB_SEEKER_LOGIN"]["FORGOT_PASSWORD_EMAIL_IS_NOT_REGISTERED"]},status=200)
            except Exception as e:
                print(e)
                return Response({"status": False, "message":Message["JOB_SEEKER_LOGIN"]["UNKNOWN_ERROR"]}, status=200)
        else:
            return Response({"status": False, "message":Message["JOB_SEEKER_LOGIN"]["FORGOT_PASSWORD_FIELDS_MISSING"]}, status=200)


#This function will update the user password.
#This function will check new password is matching our standards or not
#This function will check token is expired or not
#If it is matching and token is not expired it will update the password
#If any error is coming it will send the error messages
class ChangePassword(APIView):
    def post(self, request):
        data = request.data
        if "new_password" and "token" in data.keys():
            if is_password_valid(data["new_password"]):
                try:
                    refresh = data["token"]
                    payload = jwt.decode(refresh, public_key, algorithms=['RS256'])
                    details = UserAccount.objects.get(email_id=payload["email_id"],is_job_seeker=payload["is_job_seeker"])
                    details.password = data["new_password"]
                    details.save()
                    return Response({"status": True, "message": Message["JOB_SEEKER_LOGIN"]["NEW_PASSWORD_UPDATED_SUCCESSFULLY"]}, status=200)
                except Exception as e:
                    print(e)
                    return Response({"status": False, "message":Message["JOB_SEEKER_LOGIN"]["NEW_PASSWORD_TOKEN_EXPIRED"]}, status=200)
            else:
                return Response({"status": False, "message":Message["JOB_SEEKER_LOGIN"]["PASSWORD_IS_NOT_MATCHING_STANDARDS"]}, status=200)
        else:
            return Response({"status": False, "message":Message["JOB_SEEKER_LOGIN"]["NEW_PASSWORD_FIELDS_IS_MISSING"]}, status=200)


#This function will validate the email otp 
#It will check otp is given in time(as per FRD 2 hours otp validation time)
#If otp is valid it will send success status and token(secure password updation)
class OTPValidate(APIView):
    def get(self,request):
        if 'email_id' and 'otp' in request.GET:
            otp_details = OTPVerification.objects.filter(verification_type="email_id",verification_id=request.GET["email_id"],otp=request.GET["otp"],otp_status="N")
            otp_serilizer = OTPVerificationSerializer(otp_details, many=True).data
            if otp_serilizer:
                timestamp = int(time.time()*1000)-(120*60*1000)
                db_timestamp = int(otp_serilizer[0]["timestamp"])
                if timestamp <= db_timestamp:
                    exp = datetime.datetime.utcnow() + datetime.timedelta(minutes=10)
                    otp_details = OTPVerification.objects.get(verification_type="email_id",verification_id=request.GET["email_id"],otp=request.GET["otp"],otp_status="N")
                    otp_details.otp_status = "V"
                    otp_details.save()
                    payload = {"iat":datetime.datetime.utcnow(),"exp":exp,"email_id":otp_serilizer[0]['verification_id'],"is_job_seeker":1}
                    refresh_token = jwt.encode(payload,private_key,algorithm='RS256')
                    return Response({"status": True, "message":Message["JOB_SEEKER_LOGIN"]["EMAIL_OTP_SUCCESS"],"token":refresh_token}, status=200)
                else:
                    otp_details = OTPVerification.objects.get(verification_type="email_id",verification_id=request.GET["email_id"],otp=request.GET["otp"],otp_status="N")
                    otp_details.otp_status = "E"
                    otp_details.save()
                    return Response({"status": False, "message":Message["JOB_SEEKER_LOGIN"]["EMAIL_OTP_EXPIRE"]}, status=200)
            else:
                return Response({"status": False, "message":Message["JOB_SEEKER_LOGIN"]["OTP_IS_WRONG"]}, status=200)
        else:
            return Response({"status": False, "message":Message["JOB_SEEKER_LOGIN"]["OTP_FIELDS_MISSING"]}, status=200)

       