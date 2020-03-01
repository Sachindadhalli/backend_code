#All employer registration APIViews will be in this file
from rest_framework.views import APIView
from rest_framework.response import Response
from employer.serializers import *
from employer.models import *
from pinkjob.utils import *
from django.shortcuts import render_to_response
from django.http import HttpResponse
from django.db.models import Q
import jwt
import datetime
from pinkjob.server_settings import *
base_url = server_settings["base_url"]
#This function will check email id is exists in database or not
#It will take email_id and extra one parameter(is_employer or is_job_seeker)
def check_email_in_database(email_id):
    query = UserAccount.objects.filter(email_id=email_id,is_employer=1,is_email_verified=1)
    serializer = EmployerSerializer(query, many=True).data
    print(serializer);
    # result =[]
    # for value in serializer:
    #     tmp = {}
    #     print(value)
    #     for (index, column) in enumerate(value):
    #         #print(index,column,serializer[0][column])
    #         tmp[column] = value[column]
    #     result.append(tmp)
    # print(result)

    if serializer:
        return False
    else:
        return True    
def check_email_in_database_without_verification(email_id):
    query = UserAccount.objects.filter(email_id=email_id,is_employer=1)
    serializer = EmployerSerializer(query, many=True).data
    #print(serializer);
    # result =[]
    # for value in serializer:
    #     tmp = {}
    #     print(value)
    #     for (index, column) in enumerate(value):
    #         #print(index,column,serializer[0][column])
    #         tmp[column] = value[column]
    #     result.append(tmp)
    # print(result)

    if serializer:
        return False
    else:
        return True

#This class will verify the given email id is register as employer or not
class EmailVerification(APIView):
    def get(self, request):
        if 'email_id' in request.GET:
            try:
                if check_email_in_database(request.GET["email_id"]):
                    return Response({"status":True, "message":Message["EMPLOYER_REGISTRATION"]["EMAIL_ID_AVAILABLE_TO_USE"]},status=200) 
                else:
                    return Response({"status":False, "message":Message["EMPLOYER_REGISTRATION"]["EMAIL_ID_ALREADY_REGISTERED"]},status=200)
            except Exception as e:
                print(e)
                return Response({"status": False, "message":Message["EMPLOYER_LOGIN"]["UNKNOWN_ERROR"]}, status=200)
        else:
            return Response({"status": False, "message":Message["EMPLOYER_REGISTRATION"]["EMAIL_VERIFICATION_FIELD_IS_MISSING"]}, status=200)


#This class will create emploer account with given details(email_id,password)
#It will validate employer signup form according to FRD(email_id and password(8-20,one alphabet and one number atleast))
#If the validation is success  it will check in DB with given email id
#If the given email id is not in db it will create employer account
#After account creation it will send a link to mail to verify email
#In the link jwt token(in the token email id will attach) is added to validate email id 
class JoinRecruiter(APIView):
    def post(self,request):
        data = request.data
        validate_form = validate_login_form(data)
        print(validate_form['status'])
        if validate_form['status']:
            if check_email_in_database(data["email_id"]):
                #if check_email_in_database_without_verification(data["email_id"]):
                # UserAccount.objects.filter(Q(email_id=data["email_id"]) & Q(is_employer=1)).update_or_create(defaults={"email_id":data["email_id"] ,"password":data["password"],"is_employer":1})
                UserAccount.objects.update_or_create(email_id=data["email_id"],is_employer=1,defaults={"email_id":data["email_id"] ,"password":data["password"],"is_employer":1,"is_email_verified":0})
                private_key = open('jwt-key').read()
                public_key = open('jwt-key.pub').read()
                exp = datetime.datetime.utcnow() + datetime.timedelta(minutes=60)
                payload = {"iat":datetime.datetime.utcnow(),"exp":exp,"email_id":data["email_id"],"user_type":1}
                token = jwt.encode(payload,private_key,algorithm='RS256')
                print(token.decode("utf-8") )
                url = server_settings["api_base_url"]+"/pinkjob/employer-registration/verify-email/?token="+token.decode("utf-8") 
                body = "Hi '"+data["email_id"]+"',<br><br>Thank you for signing up with Shenzyn recruiter zone.<br><br>To complete the setup, click <a href='"+url+"'>here</a> to verify your email address.<br><br>After you're verified, you can sign in to your 'Shenzyn' Account at '"+base_url+"'. Please bookmark this URL now.<br><br>If you have questions, contact our Customer Service team.<br><br>Your Shynzyn team"
                subject = "Verify Email with shenzyn"
                send_email(subject,body,"gupta@selekt.in",[data["email_id"]])
                return Response({"status": True, "message": Message["EMPLOYER_REGISTRATION"]["JOIN_RECRUITER_SUCCESS"]}, status=200)
            else:
                return Response({"status": False, "message":Message["EMPLOYER_REGISTRATION"]["EMAIL_ID_ALREADY_REGISTERED"]}, status=200)    
        else:
            return Response({"status": False, "message":validate_form['reason']}, status=200)

#This class will call when user clicks on email verfication link
#If the token is present in request parameters will decode by using public key
#After decode it will update the db column is_email_verified as 1 and return some html render
class VerifyEmail(APIView):
    def get(self, request):
        if "token" in request.GET:
            public_key = open('jwt-key.pub').read()
            try:
                payload = jwt.decode(request.GET["token"], public_key, algorithms=['RS256'])
                email_id = payload["email_id"]
                is_employer = payload["user_type"]
                details = UserAccount.objects.get(email_id=email_id,is_employer=is_employer)
                details.is_email_verified = 1
                details.save()
                url = base_url
                return HttpResponse("<p>Email ID is verified successfully. Please click <a href='"+url+"'>here</a> to login.</p>")
            except Exception as e:
                subject = "Error in VerifyEmail"
                body = "<p>"+str(e)+"</p>"
                send_email(subject,body,"gupta@selekt.in",["gupta@selekt.in"])
                return HttpResponse("<p>Something went wrong</p>")
        else:
            return HttpResponse("<p>Something went wrong</p>")

        



  