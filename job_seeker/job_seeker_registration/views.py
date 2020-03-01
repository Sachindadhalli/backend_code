# This file contains personal details page API's for Job seeker registration. 
#The apis are Email verification, mobile otp send resend, mobile otp validation. 

from rest_framework.views import APIView
from rest_framework.response import Response
from job_seeker.services import *
from job_seeker.serializers import *
from django.db.models import Q
from pinkjob.validator import validate_file_size
import time
import datetime
from pinkjob.server_settings import *
base_url = server_settings["base_url"]
private_key = open('jwt-key').read()
public_key = open('jwt-key.pub').read()


# This is Email verification api which will check in database email is allready exist or not.
# If email is allready exist then sends status as false and message as email is allready registered with us.
# If email is not registered with us then sends status as true and message as email is available to use.
class EmailVerification(APIView):
    def get(self, request):
        try:
            if 'email_id' in request.GET:
                event_id = request.GET["email_id"]
            else:
                return Response({"status": False, "message":Message["JOB_SEEKER_REGISTRATION"]["PLEASE_ENTER_EMAIL"]}, status=200)
            if is_email_valid(event_id):
                queryset_email = UserAccount.objects.filter(Q(email_id=event_id) & Q(is_job_seeker=1) & Q(is_email_verified=0))
                serializer = UserAccountSerializer(queryset_email, many=True).data
                if serializer:
                    return Response({"status":False, "message":Message["JOB_SEEKER_REGISTRATION"]["EMAIL_ID_ALREADY_REGISTERED"]},status=200)
                else:
                    return Response({"status":True, "message":Message["JOB_SEEKER_REGISTRATION"]["EMAIL_ID_AVAILABLE_TO_USE"]},status=200)
            else:
                return Response({"status":False,"message":Message["JOB_SEEKER_REGISTRATION"]["PLEASE_ENTER_VALID_EMAIL"]},status=200)
        except Exception as e:
            return Response({"status": False, "message":format(e)}, status=200)
            
##This is use send the otp to requested mobile number for mobile verification
# Firstly it checks is that phone is valid or not then it send otp to user and save entry in database 
class MobileOTPSend(APIView):
    def post(self, request):
        try:
            req=request.data
            if is_valid_phone(req["mobile_no"]):
                if req["otp_state"] == "send":
                    OTP_send(req)
                    return Response({"status": True, "message": Message["JOB_SEEKER_REGISTRATION"]["OTP_SEND"]},status=200)
                elif req["otp_state"] == "resend":
                    OTP_send(req)
                    return Response({"status": True, "message": Message["JOB_SEEKER_REGISTRATION"]["OTP_SEND"]},status=200)
                else:
                    return Response({"status": False, "message": Message["JOB_SEEKER_REGISTRATION"]["ERROR_OTP_SEND"]},
                                    status=200)
            else:
                return Response({"status": False, "message": Message["JOB_SEEKER_REGISTRATION"]["ENTER_VALID_NUMBER"]},
                                status=200)
        except Exception as e:
            return Response({"status": False, "message": format(e)}, status=200)

# This is Mobile verification api which will compare otp with previously sended otp is match or not
# firstly check otp timestamp is exceed 30 sec or not if yes then send status false and message as otp expired
# if not then it check in database otp valid or not and depending on validation it will send status
class MobileOTPVerification(APIView):
    def post(self,request):
        try:
            req=request.data
            queryset_MobileOTP = OTPVerification.objects.filter(Q(verification_id=req["mobile_no"]) & Q(
                verification_type="number")).order_by('-id')[:1]
            serializer = OTPVerificationSerializer(queryset_MobileOTP, many=True).data
            if serializer:
                timestamp = int(time.time()*1000)-(60*1000)
                db_timestamp = int(serializer[0]["timestamp"])
                if timestamp <= db_timestamp:
                    if serializer[0]["otp"] == int(req["otp_number"]) and serializer[0]["otp_status"] == "N":
                        queryset_MobileOTP[0].otp_status = "V"
                        queryset_MobileOTP[0].save()
                        exp = datetime.datetime.utcnow() + datetime.timedelta(minutes=60)
                        payload = {"iat":datetime.datetime.utcnow(),"exp":exp,"number":req["mobile_no"]}
                        access_token = jwt.encode(payload,private_key,algorithm='RS256')
                        return Response({"status":True, "message":Message["JOB_SEEKER_REGISTRATION"]["VALID_OTP"], "token":access_token},status=200)                    
                    else:
                        return Response({"status":False, "message":Message["JOB_SEEKER_REGISTRATION"]["INVALID_OTP"]},status=200)
                else:
                    queryset_MobileOTP[0].otp_status = "E"
                    queryset_MobileOTP[0].save()
                    return Response({"status":False, "message":Message["JOB_SEEKER_REGISTRATION"]["EXPIRED_OTP"]},status=200)
            else:
                return Response({"status":False, "message":Message["JOB_SEEKER_REGISTRATION"]["INVALID_OTP"]},status=200)
        except Exception as e:
            return Response({"status": False, "message":format(e)}, status=200)


# This is Aadhar verification api - (this is just structure for api and still on Process)
class AadharCardVerification(APIView):
    def post(self,request):
        try:
            req = request.data
            return Response({"status":False, "message":Message["JOB_SEEKER_REGISTRATION"]["VALID_AADHAR"]},status=200)
        except Exception as e:
            return Response({"status": False, "message":format(e)}, status=200)



class StoreAadharCard(APIView):
    def post(self,request):
        try:
            req = request.data
            if validate_file_size(request.data["document"], 1024 * 1024 * 2):
                return Response({"status": True, "message": Message["UPDATE_PROFILE_EXCEED_FILE_SIZE"]}, status=200)
            queryset = AadharCardDeatils.objects.create(**{"path":req["document"]})
            serialiser_data = AadharCardDeatilsSerialiser(queryset).data
            file_data = serialiser_data["path"]
            return Response({"status":False, "message":"success","data":file_data},status=200)
        except Exception as e:
            return Response({"status": False, "message":format(e)}, status=200)
