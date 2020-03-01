# All employer registration APIViews will be in this file
from rest_framework.views import APIView
from .homepage_serializers import *
from .homepage_models import *
from employer.serializers import *
from job_seeker.models import OTPVerification, Designation
from job_seeker.serializers import OTPVerificationSerializer
from pinkjob.utils import *
from pinkjob.validator import validate_file_size
from django.db.models import Q
from job_seeker.services import OTP_send, is_valid_phone
from pinkjob.server_settings import *
from employer.decorators import *
from .homepage_utils import *

base_url = server_settings["base_url"]


# This function stores the employer know about information.
# The information within Recruitment Consultant / Company Recruiter / Acquisition Manager / Entrepreneur / Freelancer
# this function check is about info allready exist or not if yes then update or else create.
class KnowAboutEmployer(APIView):
    @permission_required()
    def get(self, request):
        try:
            user_id = request.META["user_id"]
            user_type = request.META["user_type"]
            if 'about_employer' in request.GET:
                queryset_user_data = EmployerProfile.objects.filter(user_account_id=user_id)
                if queryset_user_data:
                    queryset_user_data[0].about_employer = request.GET["about_employer"]
                    queryset_user_data[0].save()
                else:
                    EmployerProfile.objects.create(
                        **{"user_account_id_id": user_id, "about_employer": request.GET["about_employer"]})
                return Response(
                    {"status": True, "message": Message["EMPLOYER_HOMEPAGE"]["KNOW_ABOUT_EMPLOYER_SUCCESS"]},
                    status=200)
            else:
                return Response({"status": False, "message": Message["EMPLOYER_HOMEPAGE"]["KNOW_ABOUT_EMPLOYER_ERROR"]},
                                status=200)
        except Exception as e:
            return Response({"status": False, "message": format(e)}, status=200)


# This function check in db is email and phone number registered with us or not for only one account
# if yes then send otp, if not then send error message
class SendAccountValidateOtp(APIView):
    @permission_required()
    def get(
            self,request):
        try:
            if 'email_id' in request.GET and 'mobile_no' in request.GET and 'country_code' in request.GET:
                queryset_user_data = UserAccount.objects.filter(
                    Q(email_id=request.GET["email_id"]) & Q(is_employer=1) & Q(mobile_number=request.GET["mobile_no"]))
                if queryset_user_data:
                    OTP_send({"mobile_no": request.GET["mobile_no"], "country_code": request.GET["country_code"]})
                    return Response({"status": True, "message": Message["EMPLOYER_HOMEPAGE"]["OTP_SEND"]}, status=200)
                else:
                    return Response(
                        {"status": False, "message": Message["EMPLOYER_HOMEPAGE"]["ENTER_VALID_EMAIL_OR_NUMBER"]},
                        status=200)
            else:
                return Response({"status": False, "message": Message["EMPLOYER_HOMEPAGE"]["OTP_SEND_ERROR"]},
                                status=200)
        except Exception as e:
            return Response({"status": False, "message": format(e)}, status=200)


# This function validate otp if otp validate then it is getting employer info from database and sending through api res
# If otp enter after 30 sec the api respond otp expired
# If otp entered is invalid then it is showing otp invalid
class VerifyOTPAndPoputateDetails(APIView):
    @permission_required()
    def get(self, request):
        try:
            user_id, user_type = request.META["user_id"], request.META["user_type"]
            if 'email_id' in request.GET and 'mobile_no' in request.GET and 'country_code' in request.GET and 'otp' in request.GET:
                queryset_MobileOTP = OTPVerification.objects.filter(
                    Q(verification_id=request.GET["mobile_no"]) & Q(verification_type="number")).order_by('-id')[:1]
                serializer = OTPVerificationSerializer(queryset_MobileOTP, many=True).data
                if serializer:
                    timestamp = int(time.time()*1000)-(120*1000)
                    db_timestamp = int(serializer[0]["timestamp"])
                    if timestamp <= db_timestamp:
                        if (serializer[0]["otp"] == int(request.GET["otp"]) and serializer[0]["otp_status"] == "N"):
                            queryset_MobileOTP[0].otp_status = "V"
                            queryset_MobileOTP[0].save()
                            populate_data = {"basic_details": {}, "contact_details": {}, "work_experience": []}
                            queryset_user_data = UserAccount.objects.filter(
                                Q(email_id=request.GET["email_id"]) & Q(is_employer=1) & Q(
                                    mobile_number=request.GET["mobile_no"])).order_by('-id')[:1]
                            user_account_serializer = EmployerSerializer(queryset_user_data, many=True).data
                            for data in user_account_serializer:
                                profile = EmployerProfile.objects.get(user_account_id=data["id"])
                                user_exp_serializer = EmployerProfileSerializer(profile).data
                                city_name, country_name = "", ""
                                if user_exp_serializer["current_country"] is not None:
                                    location_data = Location.objects.get(id=user_exp_serializer["current_country"])
                                    city_name, country_name = location_data.city, location_data.country
                                basic_details = {
                                    "first_name": data["first_name"],
                                    "last_name": data["last_name"],
                                    "profile_pic_url": data["profile_image_path"],
                                    "country": country_name,
                                    "city": city_name
                                }
                                contact_details = {
                                    "mobile_prefix": data["country_code"],
                                    "mobile_number": data["mobile_number"],
                                    "secondary_email": user_exp_serializer["secondary_email"],
                                    "facebook_url": user_exp_serializer["facebook_url"],
                                    "linkedin_url": user_exp_serializer["linkedin_url"]
                                }
                                populate_data["basic_details"] = basic_details
                                populate_data["contact_details"] = contact_details
                                UserAccount.objects.filter(id=user_id).update(
                                    **{"first_name": data["first_name"], "last_name": data["last_name"],
                                       "profile_image_path": data["profile_image_path"],
                                       "country_code": data["country_code"], "mobile_number": data["mobile_number"]})
                                EmployerProfile.objects.update_or_create(user_account_id=user_id,
                                                                         defaults={"user_account_id_id": user_id,
                                                                                   "current_city_id":
                                                                                       user_exp_serializer[
                                                                                           "current_city"],
                                                                                   "current_country_id":
                                                                                       user_exp_serializer[
                                                                                           "current_country"],
                                                                                   "secondary_email":
                                                                                       user_exp_serializer[
                                                                                           "secondary_email"],
                                                                                   "facebook_url": user_exp_serializer[
                                                                                       "facebook_url"],
                                                                                   "linkedin_url": user_exp_serializer[
                                                                                       "linkedin_url"]})
                                break
                            queryset_user_exp = EmployerWorkExperience.objects.filter(
                                user_account_id=user_account_serializer[0]["id"])
                            user_exp_serializer = EmployerWorkExperienceSerializer(queryset_user_exp, many=True).data
                            exp = []
                            for data in user_exp_serializer:
                                print("---------------",data)
                                designation_name, employer_name = "", ""
                                if data["designation_id"] is not None:
                                    designation_name = Designation.objects.filter(id=data["designation_id"])[0].name
                                if data["organization_id"] is not None:
                                    employer_name = Organizations.objects.filter(id=data["organization_id"])[0].name
                                exp.append({"designation":designation_name,"employer":employer_name, "job_profile":data["description"],"join_in":data["start_date"],"left_on":data["end_date"]})
                                EmployerWorkExperience.objects.create(**{"description":data["description"],"designation_id_id":data["designation_id"],"organization_id_id":data["organization_id"],"user_account_id_id":user_id,"end_date":data["end_date"],"start_date":data["start_date"]})
                            populate_data["work_experience"] = exp                      
                            return Response({"status":True, "message":Message["EMPLOYER_HOMEPAGE"]["VALID_OTP"],"data1":user_exp_serializer, "data":populate_data},status=200)
                        else:
                            return Response({"status": False, "message": Message["EMPLOYER_HOMEPAGE"]["INVALID_OTP"]},
                                            status=200)
                    else:
                        queryset_MobileOTP[0].otp_status = "E"
                        queryset_MobileOTP[0].save()
                        return Response({"status": False, "message": Message["EMPLOYER_HOMEPAGE"]["EXPIRED_OTP"]},
                                        status=200)
                else:
                    return Response({"status": False, "message": Message["EMPLOYER_HOMEPAGE"]["INVALID_OTP"]},
                                    status=200)
            else:
                return Response({"status": False, "message": Message["EMPLOYER_HOMEPAGE"]["VERIFY_OTP_ERROR"]},
                                status=200)
        except Exception as e:
            return Response({"status": False, "message": format(e)}, status=200)


# This api used for get basic profile details of employer
# This api get user name, counrty, city, designation and employer from database
class GetBasicProfileDetails(APIView):
    @permission_required()
    def get(self, request):
        try:
            user_id, user_type, data1 = request.META["user_id"], request.META["user_type"], {}
            profile = EmployerProfile.objects.filter(user_account_id=user_id)
            serialiser_data = EmployerBasicProfileDetailsSerializer(profile, many=True).data
            for data in serialiser_data:
                data1 = {
                    "first_name": data["user_account_id"]["first_name"] + " " + data["user_account_id"]["last_name"],
                    "profile_pic_url": data["user_account_id"]["profile_image_path"],
                    "country": {"value":data["current_country"]["country"],"key":data["current_country"]["id"]} if data["current_country"] else {},
                    "city": {"value":data["current_city"]["city"],"key":data["current_city"]["id"]} if data["current_city"] else {},
                    "current_designation":{"key":data["designation_id"]["id"],"value":data["designation_id"]["name"]}  if data["designation_id"] else {},
                    "current_employer": {"value":data["organization_id"]["name"],"key":data["organization_id"]["id"]} if data["organization_id"] else {}
                }
            return Response(
                {"status": True, "message": Message["EMPLOYER_HOMEPAGE"]["BASIC_PROFILE_SUCCESS"], "data": data1},
                status=200)
        except Exception as e:
            return Response({"status": False, "message": format(e)}, status=200)


# This api used for update profile details of employer
# updated details are first name, last name, profile data, country, city, designation,employer
class UpdateBasicProfileDetails(APIView):
    @permission_required()
    def post(self, request):
        try:
            print(request.data)
            user_id, user_type, user_data, profile_data = request.META["user_id"], request.META["user_type"], {}, {}
            if 'first_name' and 'last_name' and 'profile_pic_data' and 'country' and 'city' and 'current_designation' and 'current_employer' in request.data:
                print(request.data["profile_pic_data"].size)
                if request.data["first_name"] is not "":
                    names = request.data["first_name"].split()
                    if len(names) == 1:
                        user_data["first_name"] = names[0]
                        user_data["last_name"] = ""
                    if len(names) > 1:
                        user_data["first_name"] = " ".join(names[:-1])
                        user_data["last_name"] = names[-1]
                if 'profile_pic_data' in request.data:
                    if request.data["profile_pic_data"] is not "":
                        if validate_file_size(request.data["profile_pic_data"], 1024*1024*2):
                            return Response({"status": True, "message": Message["UPDATE_PROFILE_EXCEED_FILE_SIZE"]},status=200)
                        user_data["profile_image_path"] = request.data["profile_pic_data"]
                if request.data["country"] is not "":
                    profile_data["current_country_id"] = request.data["country"]
                if request.data["city"] is not "":
                    profile_data["current_city_id"] = request.data["city"]
                if request.data["current_designation"] is not "":
                    profile_data["designation_id_id"] = update_new_values_homepage(Designation, request.data["current_designation"], "name")
                if request.data["current_employer"] is not "":
                    profile_data["organization_id_id"] = update_new_values_homepage(Organizations, request.data["current_employer"], "name")
                UserAccount.objects.update_or_create(id=user_id, defaults=user_data)
                if EmployerProfile.objects.filter(user_account_id=user_id):
                    EmployerProfile.objects.filter(user_account_id=user_id).update(**profile_data)
                else:
                    profile_data["user_account_id_id"]=user_id
                    EmployerProfile.objects.create(**profile_data)
                return Response({"status": True, "message": Message["EMPLOYER_HOMEPAGE"]["UPDATE_PROFILE_SUCCESS"]},
                                status=200)
            else:
                return Response({"status": False, "message": Message["EMPLOYER_HOMEPAGE"]["UPDATE_PROFILE_ERROR"]},
                                status=200)
        except Exception as e:
            return Response({"status": False, "message": format(e)}, status=200)


# This api used for get customise urls for employer
# This api first check is user search url length is exceed 30 character or not
# If not then it create 4 different urls for user
class GetUrlSuggestions(APIView):
    @permission_required()
    def get(self, request):
        try:
            user_id, user_type = request.META["user_id"], request.META["user_type"]
            if 'search' in request.GET:
                if len(request.GET["search"]) > 30:
                    return Response({"status": False, "message":Message["EMPLOYER_HOMEPAGE"]["EXCEED_LENGTH"]}, status=200)
                data_url, first, second, third,fourth=[], True,True,True,True
                queryset_email_data = UserAccount.objects.get(id=user_id)
                email_data = queryset_email_data.email_id.split('@')[0]
                for n in range(4):
                    x=0
                    while x < 1:
                        if len(request.GET["search"]) > 3:
                            if first:
                                sub_url = request.GET["search"]
                                url = base_url+"/recruiters/"+sub_url
                                first = False
                            else:
                                sub_url=get_urls(request.GET["search"],queryset_email_data.first_name,queryset_email_data.last_name,queryset_email_data.id,queryset_email_data.mobile_number[-4:])
                                url = base_url+"/recruiters/"+sub_url
                        else:
                            if first:
                                first = False
                                sub_url = email_data
                                url = base_url+"/recruiters/"+sub_url
                            else:
                                sub_url = get_urls(email_data,queryset_email_data.first_name,queryset_email_data.last_name,queryset_email_data.id,queryset_email_data.mobile_number[-4:])
                                url = base_url+"/recruiters/"+sub_url
                        if not EmployerProfile.objects.filter(customize_profile_url=sub_url):
                            x=1
                            data_url.append(url)
                if EmployerProfile.objects.filter(customize_profile_url=request.GET["search"]):
                    return Response({"status": False, "message":Message["EMPLOYER_HOMEPAGE"]["URL_ALLREADY_EXIST"], "data":data_url}, status=200)
                else:
                    return Response({"status": True, "message":Message["EMPLOYER_HOMEPAGE"]["GET_URL_SUCCESS"], "data":data_url}, status=200)
            else:
                return Response({"status": False, "message": Message["EMPLOYER_HOMEPAGE"]["GET_URL_ERROR"]}, status=200)
        except Exception as e:
            return Response({"status": False, "message": format(e)}, status=200)


# This api used for storing customise url in database
# This api first check is url length is exceed 30 character or not
# If not then it directly storing in database
class CustomiseUrl(APIView):
    @permission_required()
    def get(self, request):
        try:
            user_id, user_type = request.META["user_id"], request.META["user_type"]
            if 'url' in request.GET:
                if EmployerProfile.objects.filter(customize_profile_url=request.GET["url"]):
                    return Response({"status": False, "message": Message["EMPLOYER_HOMEPAGE"]["URL_ALLREADY_EXIST"]},
                                    status=200)
                queryset_user_profile_data = EmployerProfile.objects.get(user_account_id=user_id)
                queryset_user_profile_data.customize_profile_url = request.GET["url"]
                queryset_user_profile_data.save()
                return Response({"status": True, "message": Message["EMPLOYER_HOMEPAGE"]["CUSTOMISE_URL_SUCCESS"]},
                                status=200)
            else:
                return Response({"status": False, "message": Message["EMPLOYER_HOMEPAGE"]["CUSTOMISE_URL_ERROR"]},
                                status=200)
        except Exception as e:
            return Response({"status": False, "message": format(e)}, status=200)


# This api used for storing profile headline in database
# This api first check is headline length is exceed 300 character or not
# If not then it directly storing in database
class ProfileHeadline(APIView):
    # @permission_required()
    def get(self, request):
        try:
            # user_id, user_type = request.META["user_id"], request.META["user_type"]
            user_id =1
            if 'headline' in request.GET:
                if len(request.GET["headline"]) > 300:
                    return Response({"status": False, "message": Message["EMPLOYER_HOMEPAGE"]["EXCEED_LENGTH"]},
                                    status=200)
                queryset_user_profile_data = EmployerProfile.objects.get(user_account_id=user_id)
                queryset_user_profile_data.profile_headline = request.GET["headline"]
                queryset_user_profile_data.save()
                return Response({"status": True, "message": Message["EMPLOYER_HOMEPAGE"]["PROFILE_HEADLINE_SUCCESS"]},
                                status=200)
            else:
                return Response({"status": False, "message": Message["EMPLOYER_HOMEPAGE"]["PROFILE_HEADLINE_ERROR"]},
                                status=200)
        except Exception as e:
            return Response({"status": False, "message": format(e)}, status=200)

# This api used for storing profile headline in database
# This api first check is headline length is exceed 300 character or not
# If not then it directly storing in database
class GetProfileHeadline(APIView):
    # @permission_required()
    def get(self, request):
        try:
            # user_id, user_type = request.META["user_id"], request.META["user_type"]
            user_id =1
            queryset_user_profile_data = EmployerProfile.objects.get(user_account_id=user_id)
            return Response({"status": True, "message":Message["EMPLOYER_HOMEPAGE"]["PROFILE_HEADLINE_SUCCESS"], "data":queryset_user_profile_data.profile_headline}, status=200)
        except Exception as e:
            return Response({"status": False, "message":format(e)}, status=200)
# This api used for get industries from list on user search
# api respond with name and id
class GetIndustries(APIView):
    @permission_required()
    def get(self, request):
        try:
            user_id, user_type = request.META["user_id"], request.META["user_type"]
            if 'search' in request.GET:
                id = request.GET["search"]
            else:
                return Response({"status": False, "message": Message["EMPLOYER_HOMEPAGE"]["GET_INDUSTRIES_ERROR"]},
                                status=200)
            industries_queryset = Industries.objects.filter(name__icontains=id)
            serializer_industries = IndustriesSerializer(industries_queryset, many=True).data
            return Response({"status": True, "message": Message["EMPLOYER_HOMEPAGE"]["GET_INDUSTRIES_SUCCESS"],
                             "data": serializer_industries}, status=200)
        except Exception as e:
            return Response({"status": False, "message": format(e)}, status=200)


# This api used for get functional areas from list on user search
# api respond with name and id
class GetFunctionalAreas(APIView):
    @permission_required()
    def get(self, request):
        try:
            user_id, user_type = request.META["user_id"], request.META["user_type"]
            if 'search' in request.GET:
                id = request.GET["search"]
            else:
                return Response(
                    {"status": False, "message": Message["EMPLOYER_HOMEPAGE"]["GET_FUNCTIONAL_AREAS_ERROR"]},
                    status=200)
            functional_queryset = FunctionalAreas.objects.filter(name__icontains=id)
            serializer_functional_areas = FunctionalAreasSerializer(functional_queryset, many=True).data
            return Response({"status": True, "message": Message["EMPLOYER_HOMEPAGE"]["GET_FUNCTIONAL_AREAS_SUCCESS"],
                             "data": serializer_functional_areas}, status=200)
        except Exception as e:
            return Response({"status": False, "message": format(e)}, status=200)


# This api used for get level i hire from list on user search
#  api respond with name and id
class GetLevelIHire(APIView):
    @permission_required()
    def get(self, request):
        try:
            user_id, user_type = request.META["user_id"], request.META["user_type"]
            if 'search' in request.GET:
                id = request.GET["search"]
            else:
                return Response({"status": False, "message": Message["EMPLOYER_HOMEPAGE"]["GET_LEVEL_ONE_HIRE_ERROR"]},
                                status=200)
            queryset = LevelIHire.objects.filter(name__icontains=id)
            serializer_level_one_hire = LevelIHireSerializer(queryset, many=True).data
            return Response({"status": True, "message": Message["EMPLOYER_HOMEPAGE"]["GET_LEVEL_ONE_HIRE_SUCCESS"],
                             "data": serializer_level_one_hire}, status=200)
        except Exception as e:
            return Response({"status": False, "message": format(e)}, status=200)


# This is get contact details api for employer homepage
# in this api we send primary and seconadty emails, mobile code and
# number, facebook and linkedin urls and id to api response
# we are sending id because using id we can able to edit details in update api
class GetContactDetails(APIView):
    @permission_required()
    def get(self, request):
        try:
            user_id, user_type = request.META["user_id"], request.META["user_type"]
            queryset_user_data = UserAccount.objects.get(id=user_id)
            user_account_serializer = EmployerSerializer(queryset_user_data).data
            profile = EmployerProfile.objects.get(user_account_id=user_account_serializer["id"])
            user_profile_serializer = EmployerProfileSerializer(profile).data
            data1 = {"secondary_email": user_profile_serializer["secondary_email"],
                     "mobile_prefix": user_account_serializer["country_code"],
                     "mobile_number": user_account_serializer["mobile_number"],
                     "facebook_url": user_profile_serializer["facebook_url"],
                     "linkedin_url": user_profile_serializer["linkedin_url"],
                     "business_email": user_profile_serializer["business_email"],
                     "id": user_profile_serializer["id"]}
            return Response(
                {"status": True, "message": Message["EMPLOYER_HOMEPAGE"]["GET_CONTACT_SUCCESS"], "data": data1},
                status=200)
        except Exception as e:
            return Response({"status": False, "message": format(e)}, status=200)


# This is update contact details api for employer homepage
# in this api update primary and seconadty emails, mobile code and number, facebook and linkedin urls and id in database
class UpdateContactDetails(APIView):
    @permission_required()
    def get(self, request):
        try:
            user_id, user_type = request.META["user_id"], request.META["user_type"]
            if 'id' in request.GET and is_email_valid(request.GET["secondary_email"]):
                data_object = {}
                if request.GET["secondary_email"] is not "":
                    data_object["secondary_email"] = request.GET["secondary_email"]
                if request.GET["facebook_url"] is not "":
                    data_object["facebook_url"] = request.GET["facebook_url"]
                if request.GET["linkedin_url"] is not "":
                    data_object["linkedin_url"] = request.GET["linkedin_url"]
                EmployerProfile.objects.filter(id=request.GET["id"]).update(**data_object)
                return Response({"status": True, "message":Message["EMPLOYER_HOMEPAGE"]["UPDATE_CONTACT_DETAILS_SUCCESS"]}, status=200)
            else:
                return Response(
                    {"status": False, "message": Message["EMPLOYER_HOMEPAGE"]["UPDATE_CONTACT_DETAILS_ERROR"]},
                    status=200)
        except Exception as e:
            return Response({"status": False, "message": format(e)}, status=200)


# This function used for get user work experience from database
# depending upon user account id we send work experience details
class GetWorkExperienceDetails(APIView):
    @permission_required()
    def get(self, request):
        try:
            user_id, user_type = request.META["user_id"], request.META["user_type"]
            queryset_user_exp = EmployerWorkExperience.objects.filter(user_account_id=user_id)
            user_exp_serializer = EmployerWorkExperienceSerializer(queryset_user_exp, many=True).data
            exp = []
            for data in user_exp_serializer:
                designation_name, employer_name = "", ""
                if data["designation_id"] is not None:
                    designation_name = Designation.objects.get(id=data["designation_id"]).name
                if data["organization_id"] is not None  :
                    employer_name = Organizations.objects.get(id=data["organization_id"]).name
                exp.append({
                    "id":data["id"],
                    "is_current_job":data["is_current_job"],
                    "designation":{"key":data["designation_id"],"value":designation_name},
                    "employer":{"key":data["organization_id"],"value":employer_name},
                    "job_profile":data["description"],
                    "join_in":data["start_date"],
                    "left_on":data["end_date"]
                })
            return Response({"status": True, "message":Message["EMPLOYER_HOMEPAGE"]["GET_WORK_EXPERIENCE_SUCCESS"],"data":exp}, status=200)
        except Exception as e:
            return Response({"status": False, "message": format(e)}, status=200)


# This function used for Add user work experience to database
# while inserting in database we check current inserted data is is_current_job then we replace stored curremt job worked
# experience details to post job
class AddWorkExperienceDetails(APIView):
    @permission_required()
    def post(self, request):
        try:
            user_id, user_type = request.META["user_id"], request.META["user_type"]
            req = request.data
            if len(req) == 0:
                return Response({"status": False, "message": Message["EMPLOYER_HOMEPAGE"]["ADD_WORK_EXPERIENCE_ERROR"]},
                                status=200)
            for data in req:
                print(data);
                if 'is_current_job' in data and 'designation' in data and 'employer' in data and 'join_in' in data:
                    if data["is_current_job"]:
                        queryset_user_exp = EmployerWorkExperience.objects.filter(Q(user_account_id = user_id) & Q(is_current_job=True))
                        if queryset_user_exp:
                            if queryset_user_exp[0].end_date is None:
                                queryset_user_exp[0].end_date = data["join_in"]
                                queryset_user_exp[0].is_current_job = False
                                queryset_user_exp[0].save()
                    EmployerWorkExperience.objects.create(**{"user_account_id_id": user_id,
                                                             "is_current_job": data["is_current_job"],
                                                             "designation_id_id": update_new_values_homepage(
                                                                 Designation, data["designation"], "name"),
                                                             "organization_id_id": update_new_values_homepage(
                                                                 Organizations, data["employer"], "name"),
                                                             "description": data["job_profile"],
                                                             "start_date": data["join_in"],
                                                             "end_date": data["left_on"]
                                                             })
                else:
                    return Response(
                        {"status": False, "message": Message["EMPLOYER_HOMEPAGE"]["ADD_WORK_EXPERIENCE_ERROR"]},
                        status=200)
            return Response({"status": True, "message": Message["EMPLOYER_HOMEPAGE"]["ADD_WORK_EXPERIENCE_SUCCESS"]},
                            status=200)
        except Exception as e:
            return Response({"status": False, "message": format(e)}, status=200)


# This function used for update user work experience to database
# while updating in database we check current updating data is is_current_job then we replace stored
# curremt job worked experience details to post job
class UpdateWorkExperienceDetails(APIView):
    @permission_required()
    def patch(self, request):
        try:
            user_id, user_type = request.META["user_id"], request.META["user_type"]
            object_data = {}
            data =  request.data;
            print(data)
            if data["id"]:
                if data["is_current_job"]:
                    EmployerWorkExperience.objects.filter(Q(user_account_id=user_id) & Q(is_current_job=1)).update(**{"is_current_job":False})
                    object_data["is_current_job"] = True
                if data["designation"]:
                    object_data["designation_id_id"] = update_new_values_homepage(Designation, data["designation"], "name")
                if data["employer"]:
                    object_data["organization_id_id"] = update_new_values_homepage(Organizations, data["employer"], "name")
                if data["job_profile"]:
                    object_data["description"] = data["job_profile"]
                if data["join_in"]:
                    object_data["start_date"] = data["join_in"]
                if data["left_on"]:
                    object_data["end_date"] = data["left_on"]
                EmployerWorkExperience.objects.filter(Q(user_account_id=user_id) & Q(id=data["id"])).update(**object_data)
                return Response({"status": True, "message":Message["EMPLOYER_HOMEPAGE"]["UPDATE_WORK_EXPERIENCE_SUCCESS"]}, status=200)
            else:
                return Response(
                    {"status": False, "message": Message["EMPLOYER_HOMEPAGE"]["UPDATE_WORK_EXPERIENCE_ERROR"]},
                    status=200)
        except Exception as e:
            return Response({"status": False, "message": format(e)}, status=200)


# This api used for delete work experience from database
# once user click on delete work experience, depending on id we will delete data from database
class DeleteWorkExperienceDetails(APIView):
    @permission_required()
    def get(self, request):
        try:
            user_id, user_type = request.META["user_id"], request.META["user_type"]
            if 'id' in request.GET:
                EmployerWorkExperience.objects.filter(Q(user_account_id=user_id) & Q(id=request.GET["id"])).delete()
                return Response(
                    {"status": True, "message": Message["EMPLOYER_HOMEPAGE"]["DELETE_WORK_EXPERIENCE_SUCCESS"]},
                    status=200)
            else:
                return Response(
                    {"status": False, "message": Message["EMPLOYER_HOMEPAGE"]["DELETE_WORK_EXPERIENCE_ERROR"]},
                    status=200)
        except Exception as e:
            return Response({"status": False, "message": format(e)}, status=200)


# this is a get document api function 
# return all documents related to user depend on user_id given by request header response
class GetDocuments(APIView):
    @permission_required()
    def get(self, request):
        try:
            user_id, user_type, data_object = request.META["user_id"], request.META["user_type"], []
            # user_id, user_type, data_object = 2, 1, []
            queryset_user_docs = EmployerProfile.objects.filter(user_account_id=user_id)
            user_docs_serializer = EmployerDocumentsSerializer(queryset_user_docs, many=True).data
            for data in user_docs_serializer:
                data_object.append({"id": data["company_details_id"]["id"], "pan_id": data["company_details_id"]["pan"],
                                    "pan_doc": data["company_details_id"]["pan_file_path"],
                                    "other_doc": data["company_details_id"]["other_file_path"]})
            return Response(
                {"status": True, "message": Message["EMPLOYER_HOMEPAGE"]["GET_DOCUMENT_SUCCESS"], "data": data_object},
                status=200)
        except Exception as e:
            return Response({"status": False, "message": format(e)}, status=200)


# This is upload documents api function
# This function check first api requested documents and database stored
# documents count is less than or equal to 5 or not.
# if yes then documnets upload in database. if no then send error message back
class UploadDocuments(APIView):
    @permission_required()
    def post(self, request):
        try:
            user_id, user_type, req, data = request.META["user_id"], request.META["user_type"], request.data, {}
            # user_id, user_type, req, data = 1, 1, request.data, {}
            employer_queryset = EmployerProfile.objects.filter(user_account_id=user_id)
            if req["pan_id"] is not "":
                data["pan"] = req["pan_id"]
            if req["pan_doc"] is not "":
                if validate_file_size(req["pan_doc"], 1024 * 1024 * 2):
                    return Response({"status": True, "message": Message["UPDATE_PROFILE_EXCEED_FILE_SIZE"]},status=200)
                data["pan_file_path"] = req["pan_doc"]
            if req["other_doc"] is not "":
                if validate_file_size(req["pan_doc"], 1024 * 1024 * 2):
                    return Response({"status": True, "message": Message["UPDATE_PROFILE_EXCEED_FILE_SIZE"]},status=200)
                data["other_file_path"] = req["other_doc"]
            if employer_queryset:
                if employer_queryset[0].company_details_id is None:
                    company_details = CompanyDetails.objects.create(**data)
                    employer_queryset[0].company_details_id_id = company_details.id
                    employer_queryset[0].save()
                else:
                    CompanyDetails.objects.update_or_create(id=int(employer_queryset[0].company_details_id_id),
                                                            defaults=data)
            else:
                company_details = CompanyDetails.objects.create(**data)
                EmployerProfile.objects.create(
                    **{"user_account_id_id": user_id, "company_details_id_id": company_details.id})
            return Response({"status": True, "message": Message["EMPLOYER_HOMEPAGE"]["UPLOAD_DOCUMENT_SUCCESS"]},
                            status=200)
        except Exception as e:
            return Response({"status": False, "message": format(e)}, status=200)


# This is delete document api function
# it once user click on delete document this function delete document from database with related id 
class DeleteDocuments(APIView):
    @permission_required()
    def get(self, request):
        try:
            user_id, user_type = request.META["user_id"], request.META["user_type"]
            if 'id' and 'type' not in request.GET:
                return Response({"status": True, "message": Message["EMPLOYER_HOMEPAGE"]["DELETE_DOCUMENT_ERROR"]},
                                status=200)
            queryset_user_docs = CompanyDetails.objects.filter(id=request.GET["id"])
            if request.GET["type"] == "pan" and queryset_user_docs:
                queryset_user_docs[0].pan_file_path = ""
                queryset_user_docs[0].save()
            if request.GET["type"] == "other" and queryset_user_docs:
                queryset_user_docs[0].other_file_path = ""
                queryset_user_docs[0].save()
            return Response({"status": True, "message": Message["EMPLOYER_HOMEPAGE"]["DELETE_DOCUMENT_SUCCESS"]},
                            status=200)
        except Exception as e:
            return Response({"status": False, "message": format(e)}, status=200)


# This function is used for send mobile otp to requested user for change primarymobile number
# It will check mobile number is valid or not
# If it is valid, it will sent otp to user number
# Other wise it will return false with message
class ContactDetailsPhoneOtp(APIView):
    @permission_required()
    def get(self, request):
        try:
            if "mobile_no" and "country_code" in request.GET:
                if is_valid_phone(request.GET["mobile_no"]):
                    OTP_send({"mobile_no": request.GET["mobile_no"], "country_code": request.GET["country_code"]})
                    return Response({"status": True, "message": Message["EMPLOYER_HOMEPAGE"]["OTP_SEND"]}, status=200)
                else:
                    return Response({"status": False, "message": Message["EMPLOYER_HOMEPAGE"]["ENTER_VALID_NUMBER"]},
                                    status=200)
            else:
                return Response({"status": False, "message": Message["EMPLOYER_HOMEPAGE"]["ERROR_OTP_SEND"]},
                                status=200)
        except Exception as e:
            return Response({"status": False, "message": format(e)}, status=200)


# This function will validate the mobile number otp
# It will check otp is given in time(as per FRD 60 sec otp validation time)
# If otp is valid it will send success status and change mobile number in database
class ContactDetailsPhoneOtpValidate(APIView):
    @permission_required()
    def get(self, request):
        try:
            if 'mobile_no' and "otp" and 'country_code' in request.GET:
                if is_valid_phone(request.GET["mobile_no"]):
                    user_id, user_type = request.META["user_id"], request.META["user_type"]
                    queryset_MobileOTP = OTPVerification.objects.filter(
                        Q(verification_id=request.GET["mobile_no"]) & Q(verification_type="number")).order_by('-id')[:1]
                    if queryset_MobileOTP:
                        if int(time.time() * 1000) - (60 * 1000) <= int(queryset_MobileOTP[0].timestamp) and \
                                queryset_MobileOTP[0].otp == int(request.GET["otp"]) and queryset_MobileOTP[0].otp_status == "N":
                            queryset_MobileOTP[0].otp_status = "V"
                            queryset_MobileOTP[0].save()
                            UserAccount.objects.filter(Q(id=user_id) & Q(is_employer=True)).update(
                                **{"mobile_number": request.GET["mobile_no"],
                                   "country_code": request.GET["country_code"]})
                            return Response({"status": True, "message": Message["EMPLOYER_HOMEPAGE"]["VALID_OTP"]},
                                            status=200)
                        elif int(time.time() * 1000) - (60 * 1000) >= int(queryset_MobileOTP[0].timestamp) and \
                                queryset_MobileOTP[0].otp == int(request.GET["otp"]) and queryset_MobileOTP[
                            0].otp_status == "N":
                            queryset_MobileOTP[0].otp_status = "E"
                            queryset_MobileOTP[0].save()
                            return Response({"status": False, "message": Message["EMPLOYER_HOMEPAGE"]["EXPIRED_OTP"]},
                                            status=200)
                        else:
                            return Response({"status": False, "message": Message["EMPLOYER_HOMEPAGE"]["INVALID_OTP"]},
                                            status=200)
                    else:
                        return Response({"status": False, "message": Message["EMPLOYER_HOMEPAGE"]["INVALID_OTP"]},
                                        status=200)
                else:
                    return Response({"status": False, "message": Message["EMPLOYER_HOMEPAGE"]["ENTER_VALID_NUMBER"]},
                                    status=200)
            else:
                return Response({"status": False, "message": Message["EMPLOYER_HOMEPAGE"]["INVALID_OTP"]}, status=200)
        except Exception as e:
            return Response({"status": False, "message": format(e)}, status=200)


# This function is used for send email otp to requested user for change primary email address
# It will check email id is registed with us as  employer or not
# If it is not registered it will sent otp to user mail
# Other wise it will return false with message
class ContactDetailsEmailOtp(APIView):
    @permission_required()
    def get(self, request):
        try:
            if "email_id" not in request.GET:
                return Response({"status": False, "message": Message["EMPLOYER_HOMEPAGE"]["CONTACT_DETAILS_EMAIL_OTP_ERROR"]},status=200)
            if is_email_valid(request.GET["email_id"]):
                otp = get_random_number()
                otp = str(otp)
                data = {
                    "verification_type": "email_id",
                    "verification_id": request.GET["email_id"],
                    "otp": otp,
                    "otp_status": "N",
                    "timestamp": int(time.time() * 1000)}
                OTPVerification.objects.create(**data)
                subject = "OTP verification"
                body = "Dear "+request.GET["email_id"]+",<br><br>Please enter below OTP to verify your Shenzyn account Email address.<br><br>"+otp+"<br>Note: This OTP is valid for the next 2 hours only<br>Regards,<br>Shenzyn"
                send_email(subject,body,"gupta@selekt.in",[request.GET["email_id"]])
                return Response({"status":True, "message":Message["EMPLOYER_HOMEPAGE"]["CONTACT_DETAILS_EMAIL_OTP_SUCCESS"]},status=200)
            else:
                return Response({"status": False, "message": Message["JOB_SEEKER_REGISTRATION"]["PLEASE_ENTER_VALID_EMAIL"]},status=200)
        except Exception as e:
            return Response({"status": False, "message": format(e)}, status=200)


# This function will validate the email otp
# It will check otp is given in time(as per FRD 2 hours otp validation time)
# If otp is valid it will send success status and change primary email address
class ContactDetailsEmailOtpValidate(APIView):
    @permission_required()
    def get(self, request):
        if 'email_id' and 'otp' in request.GET:
            if not is_email_valid(request.GET["email_id"]):
                return Response({"status": False, "message":Message["JOB_SEEKER_REGISTRATION"]["PLEASE_ENTER_VALID_EMAIL"]}, status=200)
            user_id, user_type = request.META["user_id"], request.META["user_type"]
            otp_details = OTPVerification.objects.filter(verification_type="email_id",verification_id=request.GET["email_id"],otp_status="N").order_by("-id")
            if otp_details and str(otp_details[0].otp)==str(request.GET["otp"]):
                if int(time.time()*1000)-(120*60*1000) <=  int(otp_details[0].timestamp):
                    otp_details[0].otp_status = "V"
                    otp_details[0].save()
                    EmployerProfile.objects.update_or_create(
                        user_account_id=user_id,
                        defaults={
                            "user_account_id_id":user_id,
                            "business_email":request.GET["email_id"],
                            "is_business_email_verified":True
                        })
                    return Response({"status": True, "message":Message["EMPLOYER_HOMEPAGE"]["EMAIL_OTP_SUCCESS"]}, status=200)
                else:
                    otp_details[0].otp_status = "E"
                    otp_details[0].save()
                    return Response({"status": False, "message":Message["EMPLOYER_HOMEPAGE"]["EMAIL_OTP_EXPIRE"]}, status=200)
            else:
                return Response({"status": False, "message":Message["EMPLOYER_HOMEPAGE"]["OTP_IS_WRONG"]}, status=200)
        else:
            return Response({"status": False, "message":Message["EMPLOYER_HOMEPAGE"]["OTP_FIELDS_MISSING"]}, status=200)


def update_new_values_homepage(table_name, value, field_name):
    if value.isdigit():
        return value
    if value is "":
        return value
    print("+++++++++++", type(value), "++++++++++++++")
    search_type = '__icontains'
    field_nm = field_name + search_type
    info = table_name.objects.filter(**{field_nm: value})
    if info:
        return info[0].id
    else:
        new_value = table_name.objects.create(**{field_name: value})
        return new_value.id
