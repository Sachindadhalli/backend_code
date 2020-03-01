#All employer login APIView will be in this file
from rest_framework.views import APIView
from rest_framework.response import Response
from employer.serializers import *
from job_seeker.serializers import *
from employer.models import *
import requests
from job_seeker.models import *
from pinkjob.utils import *
from pinkjob.server_settings import *
from requests_oauthlib import OAuth2Session
from requests_oauthlib.compliance_fixes import linkedin_compliance_fix
from employer.employer_registration.views import check_email_in_database
import jwt
import datetime
import time
import json
from django.db.models import Q
private_key = open('jwt-key').read()
public_key = open('jwt-key.pub').read()
base_url = server_settings["base_url"]
# # It will check given email id is present in the database or not
# def check_email_in_database(email_id):
#     query = UserAccount.objects.filter(email_id=email_id,is_employer=1)
#     serializer = EmployerSerializer(query, many=True).data
#     print(serializer)
#     if serializer:
#         return False
#     else:
#         return True    

# This function will return linkedin in firstname and last name and profile pic url
# It will take linkedin user access token and based on access token it will query
def get_profile_details(access_token):
    try:
        headers = {
            "Authorization" : "Bearer "+access_token
        }
        #print(access_token)
        profile_details_url = "https://api.linkedin.com/v2/me?projection=(id,firstName,lastName,elements*(primary,type,handle~),profilePicture(displayImage~:playableStreams))";
        profile_details_request = requests.get(profile_details_url,headers=headers)
        profile_details =  json.loads(profile_details_request.text)
        #print(profile_details)
        primary_api_url = "https://api.linkedin.com/v2/clientAwareMemberHandles?q=members&projection=(elements*(primary,type,handle~))"
        primary_details_request = requests.get(primary_api_url,headers=headers)
        primary_details = json.loads(primary_details_request.text)
        print(profile_details["lastName"])
        employer_details = {}
        employer_details["last_name"] = profile_details["lastName"]["localized"]["en_US"] if 'lastName' in profile_details.keys() and 'localized' in profile_details["lastName"] and 'en_US' in profile_details["lastName"]["localized"].keys() else "";
        employer_details["first_name"] = profile_details["firstName"]["localized"]["en_US"] if 'firstName' in profile_details.keys() and 'localized' in profile_details["firstName"] and 'en_US' in profile_details["firstName"]["localized"].keys() else "";
        employer_details["profile_url"] = profile_details["profilePicture"]["displayImage~"]["elements"][len(profile_details["profilePicture"]["displayImage~"]["elements"])-1]["identifiers"][0]["identifier"] if 'profilePicture' in profile_details.keys() and 'displayImage~' in profile_details["profilePicture"].keys() and 'elements' in profile_details["profilePicture"]["displayImage~"].keys() and len(profile_details["profilePicture"]["displayImage~"]["elements"]) > 0 else "";
        employer_details["email_id"] = primary_details["elements"][0]["handle~"]["emailAddress"] if 'elements' in primary_details.keys() and len(primary_details["elements"]) > 0 and 'handle~' in primary_details["elements"][0] and "emailAddress" in primary_details["elements"][0]["handle~"].keys() else ""; 
        employer_details["access_token"] = access_token;
        print("email_id",employer_details["email_id"],primary_details["elements"][0]["handle~"]["emailAddress"])
        return {"status":True,"employer_details":employer_details}
    except Exception as e:
        print(e)
        return {"status":False,"reason":Message["EMPLOYER_LOGIN"]["UNKNOWN_ERROR"]}

def update_linkedin_details(details):
    try:
        id =0;
        query = UserAccount.objects.filter(email_id=details['email_id'],is_employer=1)
        serializer = EmployerSerializer(query, many=True).data
        if serializer:
            id = serializer[0]["id"]
            UserLinkedinDetails.objects.filter(Q(user_account_id_id=id)).update_or_create(user_account_id_id=id,access_token= details["access_token"],profile_pic_url = details["profile_url"]);
            return id;
    except Exception as e:
        return id;

def create_account_with_linked_details(details):
    try:
        UserAccount.objects.create(**{"email_id":details["email_id"],"last_name":details["last_name"],"first_name":details["first_name"],"is_employer":1})                
        id = update_linkedin_details(details)
        return id;
    except Exception as e:
        return 0;
# This function is used for login with email_id & password or token
# In this function we will check email_id and password are correct or not
# If it is correct we will send access token and refresh token
# same with refresh token 
class Login(APIView):
    def post(self, request):
        data = request.data
        if (('email_id' and 'password') or 'refresh_token') in data.keys():
            if 'password' in data.keys():
                validate_form = validate_login_form(data)
                if validate_form['status']:
                    query = UserAccount.objects.filter(email_id=data['email_id'],password=data['password'],is_employer=1)
                    serializer = EmployerSerializer(query, many=True).data
                    if serializer:
                        if serializer[0]["is_email_verified"]:
                            remember = data["remember"]
                            exp = datetime.datetime.utcnow() + datetime.timedelta(days=30) if remember==1 else datetime.datetime.utcnow() + datetime.timedelta(minutes=60)
                            payload = {"iat":datetime.datetime.utcnow(),"exp":exp,"user_id":serializer[0]['id'],"user_type":1} #0 for admin 1 for employer 3 for job seeker
                            access_token = jwt.encode(payload,private_key,algorithm='RS256')
                            exp = datetime.datetime.utcnow() + datetime.timedelta(days=30) if remember==1 else datetime.datetime.utcnow() + datetime.timedelta(minutes=120)
                            payload = {"iat":datetime.datetime.utcnow(),"exp":exp,"user_id":serializer[0]['id'],"user_type":1}
                            refresh_token = jwt.encode(payload,private_key,algorithm='RS256')
                            return Response({"status": True, "message": Message["EMPLOYER_LOGIN"]["LOGIN_SUCCESS"],"data": {"access_token": access_token, "refresh_token": refresh_token,}}, status=200)
                        else:
                            return Response({"status": False, "message":Message["EMPLOYER_LOGIN"]["LOGIN_EMAIL_ID_NOT_VERIFIED"]}, status=200)   
                    else:
                        return Response({"status": False, "message":Message["EMPLOYER_LOGIN"]["LOGIN_EMAIL_ID_PASSWORD_WRONG"]}, status=200)
                else:
                    return Response({"status": False, "message":validate_form['reason']}, status=200)
            else:
                try:
                    refresh = data["refresh_token"]
                    payload = jwt.decode(refresh, public_key, algorithms=['RS256'])
                    payload["iat"] = datetime.datetime.utcnow();
                    payload["exp"] = datetime.datetime.utcnow() + datetime.timedelta(minutes=60);
                    access_token = jwt.encode(payload, private_key, algorithm='RS256')
                    payload["iat"] = datetime.datetime.utcnow();
                    payload["exp"] = datetime.datetime.utcnow() + datetime.timedelta(minutes=120);
                    refresh_token = jwt.encode(payload, private_key, algorithm='RS256')
                    return Response({"status": True, "message": Message["EMPLOYER_LOGIN"]["LOGIN_SUCCESS"],"data": {"access_token": access_token, "refresh_token": refresh_token,}}, status=200)
                except Exception as e:
                    print(e)
                    return Response({"status": False, "message":Message["EMPLOYER_LOGIN"]["LOGIN_REFRESH_TOKEN_EXPIRED"]}, status=200)
        else:
            return Response({"status": False, "message":Message["EMPLOYER_LOGIN"]["LOGIN_FIELDS_MISSING"]}, status=200)


class LinkedinLogin(APIView):
    def get(self,request):
        return Response({"status": False, "message":"Error"}, status=200)


class LinkedinUserTokens(APIView):
    def get(self,request):
        print(request,request["data"])
        return Response({"status": False, "message":"Error"}, status=200)

class LinkedinCallback(APIView):
    def get(self,request):
        print(request)
        if 'code' in request.GET:
            code = request.GET["code"]
            url = 'https://www.linkedin.com/uas/oauth2/accessToken'
            payload = "grant_type=authorization_code&client_id="+server_settings["client_id"]+"&client_secret="+server_settings["client_secret"]+"&redirect_uri="+base_url+"/employer-login/linkedin-callback/&code="+code
            #print(payload)
            headers = {
                'Content-Type': "application/x-www-form-urlencoded"
            }
            try:
                access_token_request = requests.post(url, data=payload, headers=headers)
                data = json.loads(access_token_request.text)
                print(data)
                access_token = data["access_token"];
                print(access_token)
                user_details = get_profile_details(access_token)
                if user_details["status"]:
                    print(user_details["status"])
                    if user_details["employer_details"]["email_id"]!="":
                        if check_email_in_database(user_details["employer_details"]["email_id"]):
                            print(user_details["employer_details"]["email_id"])
                            id  = update_linkedin_details(user_details["employer_details"])                            
                        else:
                            id = create_account_with_linked_details(user_details["employer_details"])
                        remember = 0
                        print(id)
                        exp = datetime.datetime.utcnow() + datetime.timedelta(minutes=60)
                        payload = {"iat":datetime.datetime.utcnow(),"exp":exp,"user_id":id,"user_type":1} #0 for admin 1 for employer 3 for job seeker
                        access_token = jwt.encode(payload,private_key,algorithm='RS256')
                        exp = datetime.datetime.utcnow() + datetime.timedelta(minutes=120)
                        payload = {"iat":datetime.datetime.utcnow(),"exp":exp,"user_id":id,"user_type":1}
                        refresh_token = jwt.encode(payload,private_key,algorithm='RS256')
                        return Response({"status": True, "message": Message["EMPLOYER_LOGIN"]["LOGIN_SUCCESS"],"data": {"access_token": access_token, "refresh_token": refresh_token,}}, status=200)    
                    else:
                        return Response({"status": False, "message":Message["EMPLOYER_LOGIN"]["Linkedin_EMAIL_ID_NOT_EXIST"]}, status=200)
                else:
                    return Response({"status": False, "message":user_details["reason"]}, status=200)
            except Exception as e:
                return Response({"status": True})
                #print(e)
            #print(r)


        return Response({"status": False, "message":"Error"}, status=200)
class GmailLogin(APIView):
    def get(self, request):
        return Response({"status": False, "message":"Error"}, status=200)

#This function is used for send email otp to requested user for forgot password
#It will check email id is registed with us as  employer or not
#If it is registred it will sent otp to user mail
#Other wise it will return false with message
class ForgotPassword(APIView):
    def get(self, request):
        if 'email_id' in request.GET:
            try:
                print(check_email_in_database(request.GET["email_id"]))
                if not check_email_in_database(request.GET["email_id"]):
                    otp = get_random_number()
                    otp = str(otp)
                    data={"verification_type":"email_id","verification_id":request.GET["email_id"],"otp":otp,"otp_status":"N","timestamp":int(time.time()*1000)}
                    OTPVerification.objects.create(**data)
                    subject = "OTP verification"
                    body = "Dear "+request.GET["email_id"]+",<br><br>Please enter below OTP to reset your Shenzyn account password.<br><br>"+otp+"<br>Note: This OTP is valid for the next 2 hours only<br>Regards,<br>Shenzyn"
                    send_email(subject,body,"gupta@selekt.in",[request.GET["email_id"]])
                    return Response({"status":True, "message":Message["EMPLOYER_LOGIN"]["OTP_SENT_TO_EMAIL"]},status=200) 
                else:
                    return Response({"status":False, "message":Message["EMPLOYER_LOGIN"]["FORGOT_PASSWORD_EMAIL_IS_NOT_REGISTERED"]},status=200)
            except Exception as e:
                print(e)
                return Response({"status": False, "message":Message["EMPLOYER_LOGIN"]["UNKNOWN_ERROR"]}, status=200)
        else:
            return Response({"status": False, "message":Message["EMPLOYER_LOGIN"]["FORGOT_PASSWORD_FIELDS_MISSING"]}, status=200)

#This function will update the user password.
#This function will check new password is matching our standards or not
#This function will check token is expired or not
#If it is matching and token is not expired it will update the password
#If any error is coming it will send the error messages
class NewPassword(APIView):
    def post(self, request):
        data = request.data
        if "new_password" and "token" in data.keys():
            if is_password_valid(data["new_password"]):
                try:
                    refresh = data["token"]
                    payload = jwt.decode(refresh, public_key, algorithms=['RS256'])
                    print(payload)
                    details = UserAccount.objects.get(email_id=payload["email_id"],is_employer=payload["is_employer"])
                    details.password = data["new_password"]
                    details.save()
                    return Response({"status": True, "message": Message["EMPLOYER_LOGIN"]["NEW_PASSWORD_UPDATED_SUCCESSFULLY"]}, status=200)
                except Exception as e:
                    print(e)
                    return Response({"status": False, "message":Message["EMPLOYER_LOGIN"]["NEW_PASSWORD_TOKEN_EXPIRED"]}, status=200)
            else:
                return Response({"status": False, "message":Message["EMPLOYER_LOGIN"]["PASSWORD_IS_NOT_MATCHING_STANDARDS"]}, status=200)
        else:
            return Response({"status": False, "message":Message["EMPLOYER_LOGIN"]["NEW_PASSWORD_FIELDS_IS_MISSING"]}, status=200)


#This function will validate the email otp 
#It will check otp is given in time(as per FRD 2 hours otp validation time)
#If otp is valid it will send success status and token(secure password updation)
class OTPValidate(APIView):
    def get(self,request):
        if 'email_id' and 'otp' in request.GET:
            otp_details = OTPVerification.objects.filter(verification_type="email_id",verification_id=request.GET["email_id"],otp_status="N").order_by("-id")
            otp_serilizer = OTPVerificationSerializer(otp_details, many=True).data
            print(str(otp_serilizer[0]["otp"])==str(request.GET["otp"]),otp_serilizer[0]["otp"],request.GET["otp"])
            if otp_serilizer and str(otp_serilizer[0]["otp"])==str(request.GET["otp"]):
                timestamp = int(time.time()*1000)-(120*60*1000)
                db_timestamp = int(otp_serilizer[0]["timestamp"])
                print(timestamp,db_timestamp);
                if timestamp <= db_timestamp:
                    exp = datetime.datetime.utcnow() + datetime.timedelta(minutes=10)
                    otp_details = OTPVerification.objects.get(verification_type="email_id",verification_id=request.GET["email_id"],otp=request.GET["otp"],otp_status="N")
                    otp_details.otp_status = "V"
                    otp_details.save()
                    payload = {"iat":datetime.datetime.utcnow(),"exp":exp,"email_id":otp_serilizer[0]['verification_id'],"is_employer":1}
                    refresh_token = jwt.encode(payload,private_key,algorithm='RS256')
                    return Response({"status": True, "message":Message["EMPLOYER_LOGIN"]["EMAIL_OTP_SUCCESS"],"token":refresh_token}, status=200)
                else:
                    otp_details = OTPVerification.objects.get(verification_type="email_id",verification_id=request.GET["email_id"],otp=request.GET["otp"],otp_status="N")
                    otp_details.otp_status = "E"
                    otp_details.save()
                    return Response({"status": False, "message":Message["EMPLOYER_LOGIN"]["EMAIL_OTP_EXPIRE"]}, status=200)
            else:
                return Response({"status": False, "message":Message["EMPLOYER_LOGIN"]["OTP_IS_WRONG"]}, status=200)
        else:
            return Response({"status": False, "message":Message["EMPLOYER_LOGIN"]["OTP_FIELDS_MISSING"]}, status=200)
        
class FBLogin(APIView):
    def get(self, request):
        return Response({"status": False, "message":"Error"}, status=200)

