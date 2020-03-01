from requests_oauthlib.compliance_fixes import linkedin_compliance_fix
from oauth2client.client import flow_from_clientsecrets
from rest_framework.views import APIView
from rest_framework.response import Response
from employer.serializers import *
from job_seeker.serializers import *
from employer.models import *
from job_seeker.models import *
from pinkjob.utils import *
from pinkjob.server_settings import *
from django.db.models import Q
from requests_oauthlib import OAuth2Session
from googleapiclient.discovery import build
from django.http import *
from pinkjob import settings
from oauth2client.contrib import xsrfutil
from django.shortcuts import render
from httplib2 import Http
from employer.employer_registration.views import check_email_in_database 
from requests_toolbelt.utils import dump
import json
import jwt
import datetime
import time
import httplib2
import requests

private_key = open('jwt-key').read()
public_key = open('jwt-key.pub').read()
base_url = server_settings["base_url"]
################################
#   GMAIL API IMPLEMENTATION   #
################################

# CLIENT_SECRETS, name of a file containing the OAuth 2.0 information for this
# application, including client_id and client_secret, which are found
# on the API Access tab on the Google APIs
# Console <http://code.google.com/apis/console>

## this is setting variable for gmail login were scope and redirect url is defined and credentials for gmail login stored in json file
FLOW = flow_from_clientsecrets(
    settings.GOOGLE_OAUTH2_CLIENT_SECRETS_JSON,
    scope=['https://www.googleapis.com/auth/userinfo.email',"https://www.googleapis.com/auth/userinfo.profile","https://www.googleapis.com/auth/user.birthday.read","https://www.googleapis.com/auth/user.phonenumbers.read"],
    redirect_uri=base_url+'/employer-login/gmail-callback',
    prompt='consent')


## this is the gmail authentication function
## from here redirecting to gmail authentication function using above credentical. once user autherized then gmail send  user details in redirect url 
def gmail_authenticate(request):
    # storage = DjangoORMStorage(CredentialsModel, 'id', request.user, 'credential')
    credential = None
    if credential is None or credential.invalid:
        FLOW.params['state'] = xsrfutil.generate_token(settings.SECRET_KEY,request.user)
        authorize_url = FLOW.step1_get_authorize_url()
        return HttpResponseRedirect(authorize_url)

    else:
        http = httplib2.Http()
        http = credential.authorize(http)
        service = build('gmail', 'v1', http=http)
        print('access_token = ', credential.access_token)
        status = True
        return render(request, 'index.html', {'status': status})

##once frontend received user credntials on redirect url, frontend send user credtinal on this function url
## hare we first get credential in json object then check is user allready registered with us or not 
## if user is allready registered with us then we will uapdate there details or if user is not registered then we will insert user deatils in database
## after that we create tokens and sending back to frontend for login
def auth_return(request):
    try:
        get_state = bytes(request.GET.get('state'), 'utf8')
        if not xsrfutil.validate_token(settings.SECRET_KEY, get_state,
                                       request.user):
            return HttpResponseBadRequest()
        credential = FLOW.step2_exchange(request.GET.get('code'))
        b = credential._to_json([])
        a = json.loads(b)
        query = UserAccount.objects.filter(email_id=a["id_token"]["email"],is_employer=1)
        serializer = EmployerSerializer(query, many=True).data
        if not serializer:
            data2 = {"email_id":a["id_token"]["email"],"last_name":a["id_token"]["family_name"],"first_name":a["id_token"]["given_name"],"is_email_verified":1,"is_employer":1}
            user_account = UserAccount.objects.create(**data2)
            user_data  = UserAccount.objects.get(Q(email_id=a["id_token"]["email"]) & Q(is_employer=1))
            data ={"access_token":a["access_token"],"refresh_token":a["refresh_token"],"profile_pic_url":a["id_token"]["picture"],"user_account_id":user_account}
            try:
                if "profile_pic_url" in a["id_token"]:
                    data["profile_pic_url"]=a["id_token"]["picture"]
            except Exception as e:
                print(format(e))
            UserGmailLoginDetails.objects.create(**data)
            exp = datetime.datetime.utcnow() + datetime.timedelta(minutes=60)
            payload = {"iat":datetime.datetime.utcnow(),"exp":exp,"user_id":user_account.id,"user_type":1} #0 for admin 1 for employer 3 for job seeker
            access_token = jwt.encode(payload,private_key,algorithm='RS256')
            exp = datetime.datetime.utcnow() + datetime.timedelta(minutes=120)
            payload = {"iat":datetime.datetime.utcnow(),"exp":exp,"user_id":user_account.id,"user_type":1}
            refresh_token = jwt.encode(payload,private_key,algorithm='RS256')
            access_token = access_token.decode("utf-8")
            refresh_token = refresh_token.decode("utf-8")
            return JsonResponse({"status": True, "message": Message["EMPLOYER_LOGIN"]["LOGIN_SUCCESS"],"data": {"access_token": access_token, "refresh_token": refresh_token}})
        
        else:
            for user_data in UserAccount.objects.filter(Q(email_id=a["id_token"]["email"]) & Q(is_employer=1)):
                user_data.last_name =  a["id_token"]["family_name"]
                user_data.save()
                user_data.first_name = a["id_token"]["given_name"]
                user_data.save()
                break
            user_data  = UserAccount.objects.filter(Q(email_id=a["id_token"]["email"]) & Q(is_employer=1))
            serializer = EmployerSerializer(user_data, many=True).data
            user_account_id = serializer[0]["id"]
            if UserGmailLoginDetails.objects.filter(user_account_id=user_account_id):
                for user_gmail_data in UserGmailLoginDetails.objects.filter(user_account_id=user_account_id):
                    user_gmail_data.access_token = a["access_token"]
                    user_gmail_data.save()
                    user_gmail_data.refresh_token = a["refresh_token"]
                    user_gmail_data.save()
                    user_gmail_data.profile_pic_url = a["id_token"]["picture"]
                    user_gmail_data.save()
                    break
            else :
                data ={"access_token":a["access_token"],"refresh_token":a["refresh_token"],"profile_pic_url":a["id_token"]["picture"],"user_account_id_id":user_account_id}
                try:
                    if "profile_pic_url" in a["id_token"]:
                        data["profile_pic_url"]=a["id_token"]["picture"]
                except Exception as e:
                    print(format(e))
                UserGmailLoginDetails.objects.create(**data)
            exp = datetime.datetime.utcnow() + datetime.timedelta(minutes=60)
            payload = {"iat":datetime.datetime.utcnow(),"exp":exp,"user_id":user_account_id,"user_type":1} #0 for admin 1 for employer 3 for job seeker
            access_token = jwt.encode(payload,private_key,algorithm='RS256')
            exp = datetime.datetime.utcnow() + datetime.timedelta(minutes=120)
            payload = {"iat":datetime.datetime.utcnow(),"exp":exp,"user_id":user_account_id,"user_type":1}
            refresh_token = jwt.encode(payload,private_key,algorithm='RS256')
            access_token = access_token.decode("utf-8")
            refresh_token = refresh_token.decode("utf-8")
            return JsonResponse({"status": True, "message": Message["EMPLOYER_LOGIN"]["LOGIN_SUCCESS"],"data": {"access_token": access_token, "refresh_token": refresh_token}})
    except Exception as e:
        print(format(e))
        return JsonResponse({"status": False, "message": format(e)})