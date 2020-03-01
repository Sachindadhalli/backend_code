# This file contains userprofile page API's for edit user profile freshers. 
#The apis are get user name, get middle name , get last name, get email, get role and location. 
# from rest_framework.views import APIView
from django.http import HttpResponse
from django.db.models import *
from pinkjob import message
from employer.models import UserAccount

base_url = server_settings["base_url"]


class EditProfile(APIView):
    # This api is used for get designation by search query text
    def get(self, request):
        try:
            if 'id' in request.GET and 'first_name' in request.GET and 'middle_name' in request.GET and 'last_name' in request.GET and 'email_id' in request.GET:
                id = request.GET["id"]
                first_name = request.GET["first_name"]
                middle_name = request.GET["middle_name"]
                last_name = request.GET["last_name"]
                email_id = request.GET["email_id"]
            else:
                return Response({"status": False, "message":Message["JOB_SEEKER_REGISTRATION"]["GET_FIRST_NAME"]}, status=200)
            queryset_id = id.objects.filter(Q(first_name__icontains=first_name) & Q(middle__incontains=middle_name) & Q(last_name__incontains=last_name) & Q(email_id_incontains=email_id)
            #serializer = DesignationSerializer(queryset_designation, many=True).data
            return Response({"status":True, "message":Message["JOB_SEEKER_REGISTRATION"]["GET_DESIGNATION_SUCCESS"],"data":serializer},status=200)
        except Exception as e:
            return Response({"status": False, "message":format(e)}, status=200)

class Register(APIView):
    def post(self,request):
        req = request.data
        try:
            if 'is_fresher' in req:
                if is_email_valid(req["personal_details"]["email_id"]):
                    user_account = UserAccount.objects.filter(Q(email_id=req["personal_details"]["email_id"]) &
                                                              Q(is_job_seeker=1))
                    if user_account:
                        if user_account[0].is_email_verified == 0:
                            user_account.delete()
                        else:
                            return Response({"status": False,
                                             "message": Message["JOB_SEEKER_REGISTRATION"]["EMAIL_ID_ALREADY_REGISTERED"]
                                             }, status=200)
                    try:
                        public_key = open('jwt-key.pub').read()
                        access_token = req["personal_details"]["mobile_number"]
                        access_token = access_token.replace("Bearer ", "")
                    except Exception as e:
                        return Response({"status": False, "message": 'Mobile verification token has been exprire'}, status=401)
                    try:
                        decorator_data = jwt.decode(access_token, public_key, algorithm='RS256')
                        req["personal_details"]["mobile_number"] = decorator_data["number"]
                    except Exception as e:
                        req["personal_details"]["mobile_number"] = "9876543210"
                        # return Response({"status": False, "message": 'UnAuthorised'}, status=401)
                    user_account_data = {"first_name": req["personal_details"]["first_name"],
                                         "last_name": req["personal_details"]["last_name"],
                                         "email_id": req["personal_details"]["email_id"],
                                         "mobile_number": req["personal_details"]["mobile_number"],
                                         "dob": req["personal_details"]["date_of_birth"],
                                         "password": req["personal_details"]["password"],
                                         "regestration_date": int((time.time())*1000), "is_job_seeker": 1}
                    queryset_account = UserAccount.objects.create(**user_account_data)
                    user_account_id = queryset_account.id
                    skillset, eduction_details_array, experience_details_array = [],[],[]
                    if req["skills"]:
                        for skill in req["skills"]:
                            seeker_skill_set = {"user_account_id_id": user_account_id,
                                                "skill_set_id_id": update_new_values_job_seeker(SkillSet,
                                                                                                skill,
                                                                                                "skill_set_name")}
                            skillset.append(SeekerSkillSet(**seeker_skill_set))
                        if skillset:
                            SeekerSkillSet.objects.bulk_create(skillset)
                    for edu in req["education_details"]:
                        qualification_details = EducationalQualifications.objects.get(id=edu["qualification"])
                        if qualification_details.qualification_name == "10th" or qualification_details.qualification_name == "12th":
                            educational_details_data = {"user_account_id_id": user_account_id,
                                                        "degree_name_id": edu["qualification"],
                                                        "percentage": edu["percentage"],
                                                        "board_id": update_new_values_job_seeker(Boards, edu["board"],
                                                                                                 "board_name"),
                                                        "passed_out_year": edu["passed_year"],
                                                        "medium_id": update_new_values_job_seeker(Medium, edu["medium"],
                                                                                                  "medium_name")
                                                        }
                            eduction_details_array.append(EducationalDetails(**educational_details_data))
                        elif qualification_details.qualification_name == "Below 10th":
                            educational_details_data = {"user_account_id_id": user_account_id,
                                                        "degree_name_id": edu["qualification"]}
                            eduction_details_array.append(EducationalDetails(**educational_details_data))
                        else:
                            educational_details_data = {"user_account_id_id": user_account_id,
                                                        "degree_name_id": edu["qualification"],
                                                        "start_date": edu["start_date"],
                                                        "completion_date": edu["completion_date"],
                                                        "grading_system_id": edu["grading_system"],
                                                        "percentage": edu["percentage"],
                                                        "major_id": update_new_values_job_seeker(Majors,edu["major"],"major_name"),
                                                        "specialization_id": update_new_values_job_seeker(Specializations,edu["specialization"],"specialization_name"),
                                                        "university_id": update_new_values_job_seeker(Universities,
                                                                                                      edu["university"],
                                                                                                      "university_name"
                                                                                                      ),
                                                        "institute_id": update_new_values_job_seeker(Institutes,
                                                                                                     edu["institute"],
                                                                                                     "institute_name")
                                                        }
                            eduction_details_array.append(EducationalDetails(**educational_details_data))
                    if eduction_details_array:
                        EducationalDetails.objects.bulk_create(eduction_details_array)
                    seeker_profile_data = {"is_fresher":1, "user_account_id_id": user_account_id}
                    if "resume" in req:
                        document = 0
                        video = 0
                        for res in req["resume"]:
                            if 'resume_type' in res:
                                if res["resume_type"] == "document" and document == 0:
                                    document = document + 1
                                    seeker_profile_data["resume_document1"] = res["data"]
                                elif res["resume_type"] == "video" and video == 0:
                                    video = video + 1
                                    seeker_profile_data["resume_video1"] = res["data"]
                                elif res["resume_type"] == "document" and document == 1:
                                    document = document + 1
                                    seeker_profile_data["resume_document2"] = res["data"]
                                elif res["resume_type"] == "video" and video == 1:
                                    video = video + 1
                                    seeker_profile_data["resume_video2"] = res["data"]
                    if req["personal_details"]["aadhar_card_file_data"]:
                        seeker_profile_data["aadhar_url"] = req["personal_details"]["aadhar_card_file_data"]
                    if "break" in req:
                        if req["break"]["break_reason"] and req["break"]["break_duration"]:
                            seeker_profile_data["break_reason"] = req["break"]["break_reason"]
                            seeker_profile_data["break_duration"] = req["break"]["break_duration"]
                    if req["is_fresher"]:
                        seeker_profile_data["is_fresher"]=1
                        SeekerProfile.objects.create(**seeker_profile_data)
                        send_verification_email(req["personal_details"]["email_id"])
                        return Response({"status": True, "message": Message["JOB_SEEKER_REGISTRATION"]["REGISTER_SUCCESS"]},status=200)
                    else:
                        seeker_profile_data["is_fresher"]=0
                        SeekerProfile.objects.create(**seeker_profile_data)
                        for expe in req["work_details"]:
                            if expe["is_current_job"]:
                                experience_details_data = {"user_account_id_id": user_account_id,
                                                           "is_current_job": 1,
                                                           "city_id": expe["city"],
                                                           "state_id": expe["state"],
                                                           "country_id": expe["country"],
                                                           "description": expe["description"],
                                                           "start_date": expe["start_date"],
                                                           "job_title_id": update_new_values_job_seeker(Designation,
                                                                                                        expe["job_title"],
                                                                                                        "name"),
                                                           "annual_salary": expe["annual_salary"],
                                                           "company_name_id": update_new_values_job_seeker(CompanyNames,expe["company_name"],"company_name")}
                                experience_details_array.append(ExperienceDetails(**experience_details_data))
                            else:
                                experience_details_data = {"user_account_id_id": user_account_id,
                                                           "is_current_job": 0,
                                                           "start_date": expe["start_date"],
                                                           "end_date":expe["end_date"],
                                                           "job_title_id": update_new_values_job_seeker(Designation,
                                                                                                        expe["job_title"],
                                                                                                        "name"),
                                                           "company_name_id": update_new_values_job_seeker(CompanyNames, expe["company_name"],"company_name")}
                                experience_details_array.append(ExperienceDetails(**experience_details_data))
                                send_verification_email(req["personal_details"]["email_id"])
                        if experience_details_array:
                            ExperienceDetails.objects.bulk_create(experience_details_array)
                        return Response({"status": True, "message": Message["JOB_SEEKER_REGISTRATION"]["REGISTER_SUCCESS"]},status=200)
                else:
                    return Response({"status": False, "message": Message["JOB_SEEKER_REGISTRATION"]["PLEASE_ENTER_VALID_EMAIL"]},status=200)
            else :
                return Response({"status": False, "message": Message["JOB_SEEKER_REGISTRATION"]["REGISTER_ERROR"]},status=200)
        except Exception as e:
            return Response({"status": False, "message":format(e)}, status=200)
           