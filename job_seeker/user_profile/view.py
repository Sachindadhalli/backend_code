# This file contains userprofile page API's for edit user profile freshers. 
#The apis are get user name, get middle name , get last name, get email, get role and location. 
# from rest_framework.views import APIView
from rest_framework.views import APIView
from rest_framework.response import Response
from django.http import HttpResponse
from django.db.models import *
from employer.decorators import *
from job_seeker.serializers import JobSeekerSerializer
# from pinkjob import message
from employer.models import UserAccount


# class GetUserDetails(APIView):
#     @permission_required()
#     def get(self, request):
#         # try:
#             user_id = request.META["user_id"]
#             UserAccount.
#             # return Response({"status": True, "message":Message["JOB_SEEKER_REGISTRATION"]["FIRST_NAME"],"data":exp}, status=200)
#         # except Exception as e:
#             # return Response({"status": False, "message": format(e)}, status=200)

# This api used for get basic profile details of employer
# This api get user name, counrty, city, designation and employer from database
class GetUserDetails(APIView):
    @permission_required()
    def get(self, request):
        try:
            user_id, user_type, data1 = request.META["user_id"], request.META["user_type"], {}
            profile = UserAccount.objects.filter(user_account_id=user_id)
            serialiser_data = UserAccountSerializer(profile, many=True).data
            for data in serialiser_data:
                data1 = {
                    "first_name": data["user_account_id"]["first_name"],
                    "middle_name": data["user_account_id"]["middle_name"],
                    "last_name": data["user_account_id"]["last_name"],
                    "email_id": data["user_account_id"]["email_id"],
                    "profile_pic_url": data["user_account_id"]["profile_image_path"],
                    "country": {"value":data["current_country"]["country"],"key":data["current_country"]["id"]} if data["current_country"] else {},
                    "city": {"value":data["current_city"]["city"],"key":data["current_city"]["id"]} if data["current_city"] else {},
                    "current_designation":{"key":data["designation_id"]["id"],"value":data["designation_id"]["name"]}  if data["designation_id"] else {}
                }
            return Response(
                {"status": True, "message": Message["EMPLOYER_HOMEPAGE"]["UPDATE_PROFILE_SUCCESS"], "data": data1},
                status=200)
        except Exception as e:
            return Response({"status": False, "message": format(e)}, status=200)


# class PostUserDetails(APIView):
#     # @permission_required()
#     def post(self, request):
#         try:
#             query_useraccount_data = UserAccount(data=request.data)
#             return Response({"status": True, "message": "sub employer updated"}, status=200)
#         except Exception as e:
#             return Response({"status": False, "message": format(e)}, status=200)


# # class PatchUserDetails(APIView):
# #     # @permission_required()
# #     def patch(self, request):
# #         try:
# #             query_useraccount_data = UserAccount(data=request.data)
# #             return Response({"status": True, "message":Message["JOB_SEEKER_REGISTRATION"]["FIRST_NAME"],"data":exp}, status=200)
# #         except Exception as e:
# #             return Response({"status": False, "message": format(e)}, status=200)


class UploadPhoto(APIView):
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


class ResumeHeadline(APIView):
    @permission_required()
    def post(self,request):
        try:
            user_id, user_type, data1 = request.META["user_id"], request.META["user_type"], {}
            data = request.META["resume_headline"]
            # JobSeeker.objects.filter(id=jid).update(**data)
            return Response({"status": True, "message": "Successfully"}, status=200)
        except Exception as e:
            return Response({"status": False, "message": format(e)}, status=200) 

class GetResumeHeadline(APIView):
    @permission_required()
    def get(self, request):
        try:
            user_id, user_type, data1 = request.META["user_id"], request.META["user_type"], {}
            queryset_seeker_profile_data = SeekerProfile.objects.get(resume_headline =resume_headline)
            return Response({"status": True, "data":queryset_user_profile_data.profile_headline}, status=200)
        except Exception as e:
            return Response({"status": False, "message":format(e)}, status=200)
    

# class PostTechnologies(APIView):
#     def post(self, request):
#         try:
#             data = request.META["skill_name"]
#             JobSeeker.objects.order_by('skill_name')
#             return Response({"status": True, "message": "Successfully"}, status=200)
#         except Exception as e:
#             return Response({"status": False, "message": format(e)}, status=200)


# # class GetTechnologies(APIView):
# #     def get(self, request):
# #         try:
# #             queryset_seeker_profile_data = SeekerProfile.objects.get(skill_name =skill_name)
# #             return Response({"status": True, "data":queryset_user_profile_data.profile_headline}, status=200)
# #         except Exception as e:
# #             return Response({"status": False, "message":format(e)}, status=200)

# # class PostEmploymentFreshers(APIView):
# #     def Post(self, request):
# #         try:
# #             data = request.META["job_role"]
            

# # This class will create job seeker account with given details
# # (personal details,education details, work experience, resume, skills)
# # it will check in DB with given email id
# # If the given email id is not in db it will create employer account
# # After account creation it will send a link to mail to verify email
# # In the link jwt token(in the token email id will attach) is added to validate email id
# class Employment(APIView):
#     def post(self,request):
#         req = request.data
#         try:
#             if 'is_fresher' in req:
#                 if is_email_valid(req["personal_details"]["email_id"]):
#                     user_account = UserAccount.objects.filter(Q(email_id=req["personal_details"]["email_id"]) &
#                                                               Q(is_job_seeker=1))
#                     if user_account:
#                         if user_account[0].is_email_verified == 0:
#                             user_account.delete()
#                         else:
#                             return Response({"status": False,
#                                              "message": Message["JOB_SEEKER_REGISTRATION"]["EMAIL_ID_ALREADY_REGISTERED"]
#                                              }, status=200)
#                     try:
#                         public_key = open('jwt-key.pub').read()
#                         access_token = req["personal_details"]["mobile_number"]
#                         access_token = access_token.replace("Bearer ", "")
#                     except Exception as e:
#                         return Response({"status": False, "message": 'Mobile verification token has been exprire'}, status=401)
#                     try:
#                         decorator_data = jwt.decode(access_token, public_key, algorithm='RS256')
#                         req["personal_details"]["mobile_number"] = decorator_data["number"]
#                     except Exception as e:
#                         req["personal_details"]["mobile_number"] = "9876543210"
#                         # return Response({"status": False, "message": 'UnAuthorised'}, status=401)
#                     user_account_data = {"first_name": req["personal_details"]["first_name"],
#                                          "last_name": req["personal_details"]["last_name"],
#                                          "email_id": req["personal_details"]["email_id"],
#                                          "mobile_number": req["personal_details"]["mobile_number"],
#                                          "dob": req["personal_details"]["date_of_birth"],
#                                          "password": req["personal_details"]["password"],
#                                          "regestration_date": int((time.time())*1000), "is_job_seeker": 1}
#                     queryset_account = UserAccount.objects.create(**user_account_data)
#                     user_account_id = queryset_account.id
#                     skillset, eduction_details_array, experience_details_array = [],[],[]
#                     if req["skills"]:
#                         for skill in req["skills"]:
#                             seeker_skill_set = {"user_account_id_id": user_account_id,
#                                                 "skill_set_id_id": update_new_values_job_seeker(SkillSet,
#                                                                                                 skill,
#                                                                                                 "skill_set_name")}
#                             skillset.append(SeekerSkillSet(**seeker_skill_set))
#                         if skillset:
#                             SeekerSkillSet.objects.bulk_create(skillset)
#                     for edu in req["education_details"]:
#                         qualification_details = EducationalQualifications.objects.get(id=edu["qualification"])
#                         if qualification_details.qualification_name == "10th" or qualification_details.qualification_name == "12th":
#                             educational_details_data = {"user_account_id_id": user_account_id,
#                                                         "degree_name_id": edu["qualification"],
#                                                         "percentage": edu["percentage"],
#                                                         "board_id": update_new_values_job_seeker(Boards, edu["board"],
#                                                                                                  "board_name"),
#                                                         "passed_out_year": edu["passed_year"],
#                                                         "medium_id": update_new_values_job_seeker(Medium, edu["medium"],
#                                                                                                   "medium_name")
#                                                         }
#                             eduction_details_array.append(EducationalDetails(**educational_details_data))
#                         elif qualification_details.qualification_name == "Below 10th":
#                             educational_details_data = {"user_account_id_id": user_account_id,
#                                                         "degree_name_id": edu["qualification"]}
#                             eduction_details_array.append(EducationalDetails(**educational_details_data))
#                         else:
#                             educational_details_data = {"user_account_id_id": user_account_id,
#                                                         "degree_name_id": edu["qualification"],
#                                                         "start_date": edu["start_date"],
#                                                         "completion_date": edu["completion_date"],
#                                                         "grading_system_id": edu["grading_system"],
#                                                         "percentage": edu["percentage"],
#                                                         "major_id": update_new_values_job_seeker(Majors,edu["major"],"major_name"),
#                                                         "specialization_id": update_new_values_job_seeker(Specializations,edu["specialization"],"specialization_name"),
#                                                         "university_id": update_new_values_job_seeker(Universities,
#                                                                                                       edu["university"],
#                                                                                                       "university_name"
#                                                                                                       ),
#                                                         "institute_id": update_new_values_job_seeker(Institutes,
#                                                                                                      edu["institute"],
#                                                                                                      "institute_name")
#                                                         }
#                             eduction_details_array.append(EducationalDetails(**educational_details_data))
#                     if eduction_details_array:
#                         EducationalDetails.objects.bulk_create(eduction_details_array)
#                     seeker_profile_data = {"is_fresher":1, "user_account_id_id": user_account_id}
#                     if "resume" in req:
#                         document = 0
#                         video = 0
#                         for res in req["resume"]:
#                             if 'resume_type' in res:
#                                 if res["resume_type"] == "document" and document == 0:
#                                     document = document + 1
#                                     seeker_profile_data["resume_document1"] = res["data"]
#                                 elif res["resume_type"] == "video" and video == 0:
#                                     video = video + 1
#                                     seeker_profile_data["resume_video1"] = res["data"]
#                                 elif res["resume_type"] == "document" and document == 1:
#                                     document = document + 1
#                                     seeker_profile_data["resume_document2"] = res["data"]
#                                 elif res["resume_type"] == "video" and video == 1:
#                                     video = video + 1
#                                     seeker_profile_data["resume_video2"] = res["data"]
#                     if req["personal_details"]["aadhar_card_file_data"]:
#                         seeker_profile_data["aadhar_url"] = req["personal_details"]["aadhar_card_file_data"]
#                     if "break" in req:
#                         if req["break"]["break_reason"] and req["break"]["break_duration"]:
#                             seeker_profile_data["break_reason"] = req["break"]["break_reason"]
#                             seeker_profile_data["break_duration"] = req["break"]["break_duration"]
#                     if req["is_fresher"]:
#                         seeker_profile_data["is_fresher"]=1
#                         SeekerProfile.objects.create(**seeker_profile_data)
#                         send_verification_email(req["personal_details"]["email_id"])
#                         return Response({"status": True, "message": Message["JOB_SEEKER_REGISTRATION"]["REGISTER_SUCCESS"]},status=200)
#                     else:
#                         seeker_profile_data["is_fresher"]=0
#                         SeekerProfile.objects.create(**seeker_profile_data)
#                         for expe in req["work_details"]:
#                             if expe["is_current_job"]:
#                                 experience_details_data = {"user_account_id_id": user_account_id,
#                                                            "is_current_job": 1,
#                                                            "city_id": expe["city"],
#                                                            "state_id": expe["state"],
#                                                            "country_id": expe["country"],
#                                                            "description": expe["description"],
#                                                            "start_date": expe["start_date"],
#                                                            "job_title_id": update_new_values_job_seeker(Designation,
#                                                                                                         expe["job_title"],
#                                                                                                         "name"),
#                                                            "annual_salary": expe["annual_salary"],
#                                                            "company_name_id": update_new_values_job_seeker(CompanyNames,expe["company_name"],"company_name")}
#                                 experience_details_array.append(ExperienceDetails(**experience_details_data))
#                             else:
#                                 experience_details_data = {"user_account_id_id": user_account_id,
#                                                            "is_current_job": 0,
#                                                            "start_date": expe["start_date"],
#                                                            "end_date":expe["end_date"],
#                                                            "job_title_id": update_new_values_job_seeker(Designation,
#                                                                                                         expe["job_title"],
#                                                                                                         "name"),
#                                                            "company_name_id": update_new_values_job_seeker(CompanyNames, expe["company_name"],"company_name")}
#                                 experience_details_array.append(ExperienceDetails(**experience_details_data))
#                                 send_verification_email(req["personal_details"]["email_id"])
#                         if experience_details_array:
#                             ExperienceDetails.objects.bulk_create(experience_details_array)
#                         return Response({"status": True, "message": Message["JOB_SEEKER_REGISTRATION"]["REGISTER_SUCCESS"]},status=200)
#                 else:
#                     return Response({"status": False, "message": Message["JOB_SEEKER_REGISTRATION"]["PLEASE_ENTER_VALID_EMAIL"]},status=200)
#             else :
#                 return Response({"status": False, "message": Message["JOB_SEEKER_REGISTRATION"]["REGISTER_ERROR"]},status=200)
#         except Exception as e:
#             return Response({"status": False, "message":format(e)}, status=200)

# class PostTechnologies_worked(APIView):
#     def post(self, request):
#         try:
#             data = request.META["technologies"]
#             JobSeeker.objects.order_by('technologies')
#             return Response({"status": True, "message": "Successfully"}, status=200)
#         except Exception as e:
#             return Response({"status": False, "message": format(e)}, status=200)

# class GetTechnologies_worked(APIView):
#     def get(self, request):
#         try:
#             queryset_seeker_profile_data = SeekerProfile.objects.get(technologies= technologies)
#             return Response({"status": True, "data":queryset_user_profile_data.technologies}, status=200)
#         except Exception as e:
#             return Response({"status": False, "message":format(e)}, status=200)

# class PostProfileSummery(APIView):
#     def post(self, request):
#         try:
#             data = request.META["profile_summery"]
#             JobSeeker.objects.order_by('profile_summery')
#             return Response({"status": True, "message": "Successfully"}, status=200)
#         except Exception as e:
#             return Response({"status": False, "message": format(e)}, status=200)

# class GetProfileSummery(APIView):
#     def get(self, request):
#         try:
#             queryset_seeker_profile_data = SeekerProfile.objects.get(profile_summery= profile_summery)
#             return Response({"status": True, "data":queryset_user_profile_data.profile_summery}, status=200)
#         except Exception as e:
#             return Response({"status": False, "message":format(e)}, status=200)


# class PostDesiredCareer(APIView):
#     def post(self, request):
#         try:
#             data = request.META["desired_career_profile"]
#             JobSeeker.objects('desired_career_profile')
#             return Response({"status": True, "message": "Successfully"}, status=200)
#         except Exception as e:
#             return Response({"status": False, "message": format(e)}, status=200)

# class GetDesiredCareer(APIView):
#     def get(self, request):
#         try:
#             queryset_seeker_profile_data = SeekerProfile.objects.get(desired_career_profile= desired_career_profile)
#             return Response({"status": True, "data":queryset_seeker_profile_data.desired_career_profile}, status=200)
#         except Exception as e:
#             return Response({"status": False, "message":format(e)}, status=200)


# class PostProjectDetails(APIView):
#     def post(self, request):
#         try:
#             queryset_seeker_profile_data = user_account_id(data=request.data)
#             return Response({"status": True, "message": "Successfull"}, status=200)
#         except Exception as e:
#             return Response({"status": False, "message": format(e)}, status=200)


# class GetProjectDetails(APIView):
#     def get(self, request):
#         try:
#             query_useraccount_data = UserAccount.objects.all()
#             return Response({"status": True, "message":Message["JOB_SEEKER_REGISTRATION"]["FIRST_NAME"],"data":exp}, status=200)
#         except Exception as e:
#             return Response({"status": False, "message": format(e)}, status=200)


# class PatchProjectDetails(APIView):
#     def patch(self, request):
#         try:
#             query_useraccount_data = UserAccount.objects.all()
#             return Response({"status": True, "message": "Updated Successfully"}, status=200)
#         except Excep