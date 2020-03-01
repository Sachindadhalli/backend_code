from rest_framework.views import APIView
from rest_framework.response import Response
from employer.decorators import permission_required
from .post_jobs_serializers import *
from .post_jobs_models import *
from django.db.models import Q
from django.db import connection
from pinkjob.validator import validate_file_size
from pinkjob.server_settings import server_settings
from pinkjob.utils import *
from employer.employer_homepage.homepage_serializers import OrganizationsSerializer
from job_seeker.models import Majors, Specializations, EducationalQualifications, SkillSet, Designation
from job_seeker.serializers import MajorsKeyValueSerializer
import pdb


# This function is used for get previous job details contains name, time when posted and id
# This function gives 7 result with pagination count so at frontend only max 7 result shown depends on pagination count
class CurrentSimilarToPrevious(APIView):
    @permission_required()
    def get(self, request):
        try:
            user_id,user_type = request.META["user_id"],request.META["user_type"]
            if 'pagination' and 'sort' and 'search' in request.GET:
                offset, queryset_post_data, search_text = (int(request.GET["pagination"])*7)-7, "", request.GET["search"]
                if request.GET["sort"].lower() == "false":
                    queryset_post_data = PostJobs.objects.filter(Q(job_title__icontains=search_text) & Q(user_account_id=user_id)).order_by('id')[offset:offset+7]
                else:
                    queryset_post_data = PostJobs.objects.filter(Q(job_title__icontains=search_text) & Q(user_account_id=user_id)).order_by('-id')[offset:offset+7]
                serializer_data = SearchPostJobsSerializer(queryset_post_data, many=True).data
                return Response({"status": True, "message": Message["EMPLOYER_POST_JOBS"]["CURRET_SIMILLER_TO_PREVIOUS_SUCCESS"], "data": serializer_data}, status=200)
            else:
                return Response({"status": False, "message": Message["EMPLOYER_POST_JOBS"]["CURRET_SIMILLER_TO_PREVIOUS_ERROR"]}, status=200)
        except Exception as e:
            return Response({"status": False, "message": format(e)}, status=200)


# This function return all post jobs details saved in databased related to post job id and user id
# this function is used in populate details and edit post job functions
# This function only gives 4 tabs data such as job details, candidate profile, manage details, publish tab only
# For advertise my details tab there are different functions
class PopulateDetails(APIView):
    @permission_required()
    def get(self, request):
        try:
            user_id, user_type = request.META["user_id"], request.META["user_type"]
            if "id" not in request.GET:
                return Response({"status": False, "message": Message["EMPLOYER_POST_JOBS"]["POPULATE_DETAILS_ERROR"]}, status=200)
            key, data, location_object, working_objects, skill_objects,questionnaire_object, spec_object, major_object, \
            phd_spec_object, phd_major_object, org_object, is_show = request.GET["id"], {}, [], [], [], [], [], \
                                                                     [], [], [], [], False
            post_jobs_data = PostJobs.objects.filter(Q(id=key) & Q(user_account_id=user_id))
            #print(post_jobs_data[0].job_role.name);
            if not post_jobs_data:
                return Response({"status": True, "message": "", "data": []}, status=200)
            serializers_data = SearchPostJobsSerializer_1(post_jobs_data, many=True).data
            job_role_name = post_jobs_data[0].job_role.name if post_jobs_data[0].job_role else ""
            currency_name = post_jobs_data[0].currency.name if post_jobs_data[0].currency else ""
            industry_name = post_jobs_data[0].industries_id.name if post_jobs_data[0].industries_id else ""
            functional_area_name = post_jobs_data[0].functional_area_id.name if post_jobs_data[0].functional_area_id else ""
            for location_data in serializers_data[0]["job_id_location"]:
                location_object.append({"country": {"key": location_data["country_id"]["id"], "value": location_data["country_id"]["country"]},
                                        "location": {"key": location_data["city_id"]["id"], "value": location_data["city_id"]["city"]}})
            for timings in serializers_data[0]["job_id_time"]:
                working_objects.append({"shift": timings["time_type"], "start": timings["start_time"],
                                        "end": timings["end_time"]})
            for skill in serializers_data[0]["job_id_skill"]:
                skill_objects.append({"key": skill["qualities"]["key"], "value": skill["qualities"]["value"]})
            previous_major_id,previous_major_id2=0,0
            for spec_data in serializers_data[0]["job_id_qualification1"]:
                if spec_data["major_id"]["id"] is not previous_major_id:
                    major_object.append({"key":spec_data["major_id"]["id"],"value":spec_data["major_id"]["major_name"]})
                    previous_major_id = spec_data["major_id"]["id"]
                    spec_object.append({"parent_key":spec_data["major_id"]["id"], "key":spec_data["major_id"]["id"], "value":spec_data["major_id"]["major_name"], "is_parent":True})
                spec_object.append({"parent_key":spec_data["major_id"]["id"], "key":spec_data["specialization_id"]["id"], "value":spec_data["specialization_id"]["specialization_name"], "is_parent":False})
            for spec_data in serializers_data[0]["job_id_qualification2"]:
                if spec_data["phd_major_id"]["id"] is not previous_major_id2:
                    phd_major_object.append({"key":spec_data["phd_major_id"]["id"],"value":spec_data["phd_major_id"]["major_name"]})
                    previous_major_id2 = spec_data["phd_major_id"]["id"]
                    phd_spec_object.append({"parent_key":spec_data["phd_major_id"]["id"], "key":spec_data["phd_major_id"]["id"], "value":spec_data["phd_major_id"]["major_name"], "is_parent":True})
                phd_spec_object.append({"parent_key":spec_data["phd_major_id"]["id"], "key":spec_data["phd_specialization_id"]["id"], "value":spec_data["phd_specialization_id"]["specialization_name"], "is_parent":False})
            for org_data in serializers_data[0]["job_id_hide_or_show"]:
                is_show = org_data["is_show"]
                org_object.append({"key":org_data["organisation_id"]["key"],"value":org_data["organisation_id"]["value"]})
            print(org_object)
            questionnaire_queryset = JobPostQuestionnaire.objects.filter(job_id=post_jobs_data[0].id)
            for questionnaire_data in questionnaire_queryset:
                questionnaire_object = {"key": questionnaire_data.questionnaire_id.id, "value": questionnaire_data.questionnaire_id.questionnaire_name}
            advertise_key = serializers_data[0]["post_jobs_advertise_id"][0]["advertise_company_details_id"]["id"] if serializers_data[0]["post_jobs_advertise_id"] else ""
            data["job_details"] = {"title": post_jobs_data[0].job_title,
                                   "job_role": {"key": post_jobs_data[0].job_role_id,
                                                "value": job_role_name},
                                   "job_description": post_jobs_data[0].job_description,
                                   "work_experience_min": post_jobs_data[0].min_experience,
                                   "work_experience_max": post_jobs_data[0].max_experience,
                                   "is_fresher": post_jobs_data[0].is_fresher,
                                   "currency": {"key": post_jobs_data[0].currency_id,
                                                "value": currency_name},
                                   "minimum_ctc": post_jobs_data[0].min_salary,
                                   "maximum_ctc": post_jobs_data[0].max_salary,
                                   "visible_to_no_one": post_jobs_data[0].is_salary_visible,
                                   "number_of_vacancy": post_jobs_data[0].no_of_vacancies,
                                   "how_soon": post_jobs_data[0].how_soon_required,
                                   "industry": {"key": post_jobs_data[0].industries_id_id,
                                                "value": industry_name},
                                   "functional_area": {"key": post_jobs_data[0].functional_area_id_id,
                                                       "value": functional_area_name},
                                   "job_type": post_jobs_data[0].type_of_job,
                                   "status": post_jobs_data[0].status,
                                   "count": post_jobs_data[0].from_count,
                                   "locations": location_object,
                                   "timings": working_objects,
                                   "key_skills": skill_objects
                                   }
            data["candidate_profile"] = {"back_to_work": post_jobs_data[0].is_longtime_break,
                                         "show_jobs_specific_org": is_show,
                                         "majors": major_object,
                                         "specialisations": spec_object,
                                         "qual_premier_required": post_jobs_data[0].is_graduate_premium_university,
                                         "phd_majors": phd_major_object,
                                         "phd_specialisations": phd_spec_object,
                                         "phd_qual_premier_required": post_jobs_data[0].is_phd_premium_university,
                                         "candidate_profile": post_jobs_data[0].candidate_profile,
                                         "organisation_name": org_object
                                         }
            data["manage_response"] = {"email_or_walkin": post_jobs_data[0].is_email_response,
                                       "forward_application_to_email": post_jobs_data[0].is_email_forward,
                                       "selected_email": post_jobs_data[0].forward_email_id,
                                       "questioner_id": questionnaire_object,
                                       "reference_code": post_jobs_data[0].reference_code,
                                       "date_from": serializers_data[0]["job_id_walkin"][0]["start_date"] if serializers_data[0]["job_id_walkin"] else "",
                                       "date_to": serializers_data[0]["job_id_walkin"][0]["end_date"] if serializers_data[0]["job_id_walkin"] else "",
                                       "time_from": serializers_data[0]["job_id_walkin"][0]["start_time"] if serializers_data[0]["job_id_walkin"] else "",
                                       "time_to": serializers_data[0]["job_id_walkin"][0]["end_time"] if serializers_data[0]["job_id_walkin"] else "",
                                       "venue": serializers_data[0]["job_id_walkin"][0]["venue"] if serializers_data[0]["job_id_walkin"] else "",
                                       "address_url": serializers_data[0]["job_id_walkin"][0]["location_url"] if serializers_data[0]["job_id_walkin"] else ""
                                       }
            data["advertise_company_details"] = {"key":advertise_key}
            data["publish_job"] = {"refresh_time": post_jobs_data[0].schedule_time,
                                   "job_type": post_jobs_data[0].status
                                   }
            return Response({"status": True, "message": Message["EMPLOYER_POST_JOBS"]["POPULATE_DETAILS_SUCCESS"], "data":data}, status=200)
        except Exception as e:
            return Response({"status": False, "message": format(e)}, status=200)


# This function called when get currency function runs
# this function send result as key and value in key and value we sending id as key and currency symbol as value
# Also This is a search function which give search related result
class GetCurrency(APIView):
    @permission_required()
    def get(self, request):
        try:
            user_id, user_type = request.META["user_id"], request.META["user_type"]
            if 'search' in request.GET:
                currency_data = []
                queryset_currency = Currency.objects.filter(Q(name__icontains=request.GET["search"]) |
                                                            Q(code__icontains=request.GET["search"]))
                for data in queryset_currency:
                    currency_data.append({"key":data.id, "value": data.code +" "+data.symbol})
                return Response({"status": True, "message": Message["EMPLOYER_POST_JOBS"]["GET_CURRENCY_SUCCESS"], "data": currency_data}, status=200)
            return Response({"status": False, "message": Message["EMPLOYER_POST_JOBS"]["GET_CURRENCY_ERROR"]}, status=200)
        except Exception as e:
            return Response({"status": False, "message": format(e)}, status=200)


# This is a get Qualification function which will return only master/ post- graduation and graduation/ diploma majors
# this function used in candidate profile tab get qualifications
class GetQualification(APIView):
    @permission_required()
    def get(self, request):
        try:
            if 'search' in request.GET:
                id = request.GET["search"]
            else:
                return Response({"status": False, "message": Message["EMPLOYER_POST_JOBS"]["GET_QUALIFICATION_ERROR"]},
                                status=200)
            queryset = EducationalQualifications.objects.filter(Q(qualification_name__icontains=
                                                                  'masters/post-graduation') |
                                                                Q(qualification_name__icontains='graduation/diploma'))
            ids = []
            for data in queryset:
                ids.append(data.id)
            majors_queryset = Majors.objects.filter(Q(major_name__icontains=id) & Q(qualification_id__in=ids))
            majors_serializers = MajorsKeyValueSerializer(majors_queryset, many=True).data
            return Response({"status": True, "message": Message["EMPLOYER_POST_JOBS"]["GET_QUALIFICATION_SUCCESS"],
                             "data": majors_serializers}, status=200)
        except Exception as e:
            return Response({"status": False, "message": format(e)}, status=200)


# This is a get phd qualification api function which will return only phd level qualification major names
# This is function used in candidate profile table of post jobs page for get PHD Qualification details
class GetPHDQualification(APIView):
    @permission_required()
    def get(self, request):
        try:
            if 'search' in request.GET:
                id = request.GET["search"]
            else:
                return Response({"status": False, "message": Message["EMPLOYER_POST_JOBS"]["GET_PHD_QUALIFICATION_ERROR"]},
                                status=200)
            queryset = EducationalQualifications.objects.filter(qualification_name__icontains='Doctorate/PhD')
            ids = []
            for data in queryset:
                ids.append(data.id)
            majors_queryset = Majors.objects.filter(Q(major_name__icontains=id) & Q(qualification_id__in=ids))
            majors_serializers = MajorsKeyValueSerializer(majors_queryset, many=True).data
            return Response({"status": True, "message": Message["EMPLOYER_POST_JOBS"]["GET_PHD_QUALIFICATION_SUCCESS"],
                             "data": majors_serializers}, status=200)
        except Exception as e:
            return Response({"status": False, "message": format(e)}, status=200)


# This function used in get Specifications using above 2 apis(getQualifications and getPHDQualifications) selected ids
# This function returns specialisations with respected majors
class GetSpecializations(APIView):
    @permission_required()
    def post(self, request):
        try:
            if 'id' in request.data:
                id, format_data = request.data["id"], []
            else:
                return Response({"status": False, "message": Message["EMPLOYER_POST_JOBS"]["GET_SPECIALIZATION_ERROR"]},
                                status=200)
            major_queryset = Majors.objects.filter(id__in=id)
            for major in major_queryset:
                format_data.append({"parent_key": major.id, "key": major.id, "value": major.major_name, "is_parent": True})
            queryset = Specializations.objects.filter(majors_id__in=id)
            for specs in queryset:
                format_data.append({"parent_key": specs.majors_id_id, "key": specs.id, "value": specs.specialization_name, "is_parent": False})
            format_data.sort(key=get_my_key)
            print(format_data)
            return Response({"status": True, "message": Message["EMPLOYER_POST_JOBS"]["GET_SPECIALIZATION_SUCCESS"],
                             "data": format_data}, status=200)
        except Exception as e:
            return Response({"status": False, "message": format(e)}, status=200)


# This function used in get questionnaire names saved related to user id
# so that he can able to select this questionnaire for another post jobs
# This function only return questionnaire names with there respected ids
class GetQuestionnaireNames(APIView):
    @permission_required()
    def get(self, request):
        try:
            if 'search' not in request.GET:
                return Response({"status": False, "message": Message["EMPLOYER_POST_JOBS"]["GET_QUESTIONNAIRE_NAMES_ERROR"]}, status=200)
            user_id, search = request.META["user_id"], request.GET["search"]
            data_object = []
            queryset = EmployerQuestionnaire.objects.filter(user_id=user_id)
            serializer_data = EmployerQuestionnaireSerialiser(queryset, many=True).data
            for data in serializer_data:
                data_object.append({"key":data["questionnaire_id"]["id"],"value":data["questionnaire_id"]["questionnaire_name"]})
            return Response({"status": True, "message": Message["EMPLOYER_POST_JOBS"]["GET_QUESTIONNAIRE_NAMES_SUCCESS"], "data": data_object}, status=200)
        except Exception as e:
            return Response({"status": False, "message": format(e)}, status=200)


# This function used to get all questionnaire questions with options based on requested id
# This function return questionnaire name and all questions with there options
class GetQuestionnaire(APIView):
    @permission_required()
    def get(self, request):
        try:
            if 'id' not in request.GET:
                return Response({"status": False, "message": Message["EMPLOYER_POST_JOBS"]["GET_QUESTIONNAIRE_ERROR"]}, status=200)
            key, data, questions_array, options_array = request.GET["id"], {"name": "", "data": []}, [], []
            questionnaire_table = Questionnaire.objects.filter(id=key)
            serialiser_data = QuestionnaireSerialiser(questionnaire_table, many=True).data
            for values in serialiser_data:
                data["name"] = values["questionnaire_name"]
                for questions in values["questionnaire_id_questions"]:
                    mapping_queryset = QuestionOptionsMapping.objects.filter(question_id=questions["question_id"]["id"])
                    serialiser_mapping = QuestionOptionsMappingSerialiser(mapping_queryset, many=True).data
                    input_field, options_array= "", []
                    for map in serialiser_mapping:
                        if map["option_values_id"] is not None:
                            options_array.append(map["option_values_id"]["option_name"])
                        input_field = map["input_type_id"]["input_type"]
                    questions_array.append({"question": questions["question_id"]["question_text"], "is_mandatory": questions["question_id"]["is_mandatory"], "type": input_field, "options": options_array})
                data["data"]=questions_array
            return Response({"status": True, "message": Message["EMPLOYER_POST_JOBS"]["GET_QUESTIONNAIRE_SUCCESS"], "data": data}, status=200)
        except Exception as e:
            return Response({"status": False, "message": format(e)}, status=200)


# This function used to Create New questionnaire
# User can create questionnaire in frontend and frontend send data in json format
# After that we are saving data in respected tables
class CreateQuestionnaire(APIView):
    @permission_required()
    def post(self, request):
        try:
            user_id, data = request.META["user_id"], request.data
            # user_id, data = 1, request.data
            # data1 = {"name": "", "data": [{"question": "", "is_mandatory": True, "type": "", "options": []}]} request.META["user_id"]
            if data is not {}:
                questionnaire_table = Questionnaire.objects.create(**{"questionnaire_name": data["name"]})
                print("----------------------")
                for value in data["data"]:
                    questions_data = Questions.objects.create(**{"question_text": value["question"],
                                                                 "is_mandatory": value["is_mandatory"]})
                    input_type = InputType.objects.create(**{"input_type": value["type"]})
                    if value["options"]:
                        for options in value["options"]:
                            print(options,"------------------")
                            option_data = OptionValues.objects.create(**{"option_name": options})
                            QuestionOptionsMapping.objects.create(
                                **{"input_type_id_id": input_type.id, "question_id_id": questions_data.id,
                                   "option_values_id_id": option_data.id})
                    else:
                        QuestionOptionsMapping.objects.create(**{"input_type_id_id": input_type.id, "question_id_id": questions_data.id})
                    QuestionnaireQuestions.objects.create(**{"questionnaire_id_id": questionnaire_table.id,
                                                             "question_id_id": questions_data.id})
                EmployerQuestionnaire.objects.create(**{"questionnaire_id_id":questionnaire_table.id,"user_id_id":user_id})
            return Response({"status": True, "message": Message["EMPLOYER_POST_JOBS"]["CREATE_QUESTIONNAIRE_SUCCESS"]}, status=200)
        except Exception as e:
            return Response({"status": False, "message": format(e)}, status=200)


# This function used to edit the questionnaire
# For editing questionnaire it will be complex because of so many tables we are firstly delete questionnaire
# and then after again create new questionnaire same as previous function
class EditQuestionnaire(APIView):
    @permission_required()
    def post(self, request):
        try:
            user_id, data = request.META["user_id"], request.data
            # user_id, data = 1, request.data
            key, questions_array, options_array, input_array = request.data["id"], [], [], []
            questionnaire_table = Questionnaire.objects.filter(id=key)
            serialiser_data = QuestionnaireSerialiser(questionnaire_table, many=True).data
            for values in serialiser_data:
                for questions in values["questionnaire_id_questions"]:
                    mapping_queryset = QuestionOptionsMapping.objects.filter(question_id=questions["question_id"]["id"])
                    serialiser_mapping = QuestionOptionsMappingSerialiser(mapping_queryset, many=True).data
                    input_field = "",
                    for map in serialiser_mapping:
                        if map["option_values_id"] is not None:
                            options_array.append(map["option_values_id"]["id"])
                        input_field = map["input_type_id"]["id"]
                    input_array.append(input_field)
                    questions_array.append(questions["question_id"]["id"])
                Questions.objects.filter(id__in=questions_array).delete()
                OptionValues.objects.filter(id__in=options_array).delete()
                InputType.objects.filter(id__in=input_array).delete()
            if data is not {}:
                questionnaire_table = Questionnaire.objects.filter(id=key)
                questionnaire_table[0].questionnaire_name=data["name"]
                questionnaire_table[0].save()
                print("----------------------")
                for value in data["data"]:
                    questions_data = Questions.objects.create(**{"question_text": value["question"],
                                                                 "is_mandatory": value["is_mandatory"]})
                    input_type = InputType.objects.create(**{"input_type": value["type"]})
                    if value["options"]:
                        for options in value["options"]:
                            print(options, "------------------")
                            option_data = OptionValues.objects.create(**{"option_name": options})
                            QuestionOptionsMapping.objects.create(
                                **{"input_type_id_id": input_type.id, "question_id_id": questions_data.id,
                                   "option_values_id_id": option_data.id})
                    else:
                        QuestionOptionsMapping.objects.create(
                            **{"input_type_id_id": input_type.id, "question_id_id": questions_data.id})
                    QuestionnaireQuestions.objects.create(**{"questionnaire_id_id": questionnaire_table[0].id,
                                                             "question_id_id": questions_data.id})
                EmployerQuestionnaire.objects.create(
                    **{"questionnaire_id_id": questionnaire_table[0].id, "user_id_id": user_id})
            return Response({"status": True, "message": Message["EMPLOYER_POST_JOBS"]["EDIT_QUESTIONNAIRE_SUCCESS"]}, status=200)
        except Exception as e:
            return Response({"status": False, "message": format(e)}, status=200)


# This function delete Questionnaire from database related to user id and and requested questionnaire id
class DeleteQuestionnaire(APIView):
    @permission_required()
    def get(self, request):
        try:
            if 'id' not in request.GET:
                return Response({"status": False, "message":  Message["EMPLOYER_POST_JOBS"]["DELETE_QUESTIONNAIRE_ERROR"]}, status=200)
            key, questions_array, options_array, input_array = request.GET["id"], [], [], []
            questionnaire_table = Questionnaire.objects.filter(id=key)
            serialiser_data = QuestionnaireSerialiser(questionnaire_table, many=True).data
            for values in serialiser_data:
                for questions in values["questionnaire_id_questions"]:
                    mapping_queryset = QuestionOptionsMapping.objects.filter(question_id=questions["question_id"]["id"])
                    serialiser_mapping = QuestionOptionsMappingSerialiser(mapping_queryset, many=True).data
                    input_field = "",
                    for map in serialiser_mapping:
                        if map["option_values_id"] is not None:
                            options_array.append(map["option_values_id"]["id"])
                        input_field = map["input_type_id"]["id"]
                    input_array.append(input_field)
                    questions_array.append(questions["question_id"]["id"])
                Questionnaire.objects.filter(id=key).delete()
                Questions.objects.filter(id__in=questions_array).delete()
                OptionValues.objects.filter(id__in=options_array).delete()
                InputType.objects.filter(id__in=input_array).delete()
            return Response({"status": True, "message":  Message["EMPLOYER_POST_JOBS"]["DELETE_QUESTIONNAIRE_SUCCESS"]}, status=200)
        except Exception as e:
            return Response({"status": False, "message": format(e)}, status=200)


# This function use to get existing email address assign for different job post
# This function checks in post jobs table and list out all email addresses
class GetExistingEmail(APIView):
    @permission_required()
    def get(self,request):
        try:
            user_id, user_type = request.META["user_id"], request.META["user_type"]
            post_jobs_queryset = PostJobs.objects.filter(user_account_id=user_id).exclude(forward_email_id__isnull=True).values('forward_email_id').distinct()
            serialiser_data = ExistingEmailSerializer(post_jobs_queryset, many=True).data
            return Response({"status": True, "message": Message["EMPLOYER_POST_JOBS"]["GET_EXISTING_EMAILS_SUCCESS"], "data":serialiser_data}, status=200)
        except Exception as e:
            return Response({"status": False, "message": format(e)}, status=200)


# This function save all post job details in database
# This function save details for only for tabs such as job details, candidate profile, manage details and post jobs tab
class PostJob(APIView):
    @permission_required()
    def post(self, request):
        try:
            user_id, user_type = request.META["user_id"], request.META["user_type"]
            data = request.data
            response_id = data["id"]
            if data is []:
                return Response({"status": False, "message": Message["EMPLOYER_POST_JOBS"]["POST_JOBS_ERROR"]}, status=200)
            if 'job_details' in data:
                post_job_data = {"user_account_id_id": user_id, "job_title": data["job_details"]["title"],
                                 "job_role_id": update_new_values(Designation, data["job_details"]["job_role"]["key"],"name"),
                                 "job_description": data["job_details"]["job_description"],
                                 "min_experience": data["job_details"]["work_experience_min"],
                                 "max_experience": data["job_details"]["work_experience_max"],
                                 "is_fresher": data["job_details"]["is_fresher"],
                                 "currency_id": data["job_details"]["currency"]["key"],
                                 "min_salary": data["job_details"]["minimum_ctc"],
                                 "max_salary": data["job_details"]["maximum_ctc"],
                                 "is_salary_visible": data["job_details"]["visible_to_no_one"],
                                 "no_of_vacancies": data["job_details"]["number_of_vacancy"],
                                 "how_soon_required": data["job_details"]["how_soon"],
                                 "industries_id_id": update_new_values(Industries, data["job_details"]["industry"]["key"], "name"),
                                 "functional_area_id_id": update_new_values(FunctionalAreas, data["job_details"]["functional_area"]["key"], "name"),
                                 "type_of_job": data["job_details"]["job_type"], "status": "Draft",
                                 "from_count": 1}
                if data["id"] is None or data["id"] is "":
                    print("-------")
                    job_id = PostJobs.objects.create(**post_job_data)
                    response_id = job_id.id
                else:
                    job_id = PostJobs.objects.filter(id=data["id"]).update(**post_job_data)
                    response_id = data["id"]
                DesireCandidateProfileSkills.objects.filter(job_id=response_id).delete()
                WorkingHours.objects.filter(job_id=response_id).delete()
                JobLocations.objects.filter(job_id=response_id).delete()
                for location in data["job_details"]["locations"]:
                    location_data = {"country_id_id": location["country"]["key"], "job_id_id": response_id,
                                     "city_id_id": location["country"]["key"]}
                    JobLocations.objects.create(**location_data)
                for timings in data["job_details"]["timings"]:
                    shift_data = {"job_id_id": response_id, "time_type": timings["shift"], "start_time": timings["start"],
                                  "end_time": timings["end"]}
                    WorkingHours.objects.create(**shift_data)
                for skill in data["job_details"]["key_skills"]:
                    skill_data = {"job_id_id": response_id, "qualities_id":  update_new_values(SkillSet, skill["value"], "skill_set_name")}
                    DesireCandidateProfileSkills.objects.create(**skill_data)
            if 'candidate_profile' in data:
                post_job_data = {"from_count": 2, "candidate_profile": data["candidate_profile"]["candidate_profile"],
                                 "is_phd_premium_university": data["candidate_profile"]["phd_qual_premier_required"],
                                 "is_graduate_premium_university": data["candidate_profile"]["qual_premier_required"],
                                 "is_longtime_break": data["candidate_profile"]["back_to_work"]}
                # print("coming**********",post_jobs_data)
                 
                # print("coming**********",post_jobs_data)
                # post_job_data = {"from_count": 2, "candidate_profile": data["candidate_profile"]["candidate_profile"],
                #                  "is_phd_premium_university": data["candidate_profile"]["phd_qual_premier_required"],
                #                  "is_graduate_premium_university": data["candidate_profile"]["qual_premier_required"],
                #                  "is_longtime_break": data["candidate_profile"]["back_to_work"]}
                PostJobs.objects.filter(id=data["id"]).update(**post_job_data)
                print(PostJobs.objects.filter(Q(id=key) & Q(user_account_id=user_id)))
                ShowOrHideOrganisations.objects.filter(job_id=response_id).delete()
                JobRequiredQualifications.objects.filter(job_id=response_id).delete()
                JobRequiredPHDQualifications.objects.filter(job_id=response_id).delete()
                for organisations in data["candidate_profile"]["organisation_name"]:
                    organisation_data = {"organisation_id_id": update_new_values(Organizations, organisations["key"], "name"),
                                         "job_id_id": response_id,
                                         "is_show": data["candidate_profile"]["show_jobs_specific_org"]}
                    ShowOrHideOrganisations.objects.create(**organisation_data)
                for Qualifications in data["candidate_profile"]["specialisations"]:
                    if Qualifications["is_parent"]==False:
                        print("------------------------")
                        JobRequiredQualifications.objects.create(**{"major_id_id": Qualifications["parent_key"],
                                                                    "specialization_id_id": Qualifications["key"],
                                                                    "job_id_id": response_id})
                for Qualifications in data["candidate_profile"]["phd_specialisations"]:
                    if Qualifications["is_parent"] == False:
                        print("++++++++++++++++++++++++++")
                        JobRequiredPHDQualifications.objects.create(**{"phd_major_id_id": Qualifications["parent_key"],
                                                                    "phd_specialization_id_id": Qualifications["key"],
                                                                    "job_id_id": response_id})
            if 'manage_response' in data:
                post_job_data, manage_response = {}, data["manage_response"]
                if manage_response["email_or_walkin"] == "email":
                    post_job_data = {"from_count": 3, "is_email_response": True,
                                     "forward_email_id": manage_response["selected_email"],
                                     "is_email_forward": manage_response["forward_application_to_email"],
                                     "reference_code": manage_response["reference_code"]}
                else:
                    post_job_data = {"from_count": 3, "is_email_response": False,
                                     "reference_code": manage_response["reference_code"]}
                    walk_in_data = {"job_id_id": response_id, "start_date": manage_response["date_from"],
                                    "end_date": manage_response["date_to"],
                                    "start_time": manage_response["time_from"],
                                    "end_time": manage_response["time_to"], "venue": manage_response["venue"],
                                    "location_url": manage_response["address_url"]}
                    WalkinDetails.objects.update_or_create(job_id_id=response_id, defaults=walk_in_data)
                PostJobs.objects.filter(id=data["id"]).update(**post_job_data)
                questionnaire_data = {"job_id_id": response_id,
                                      "questionnaire_id_id": manage_response["questioner_id"]["key"]}
                JobPostQuestionnaire.objects.update_or_create(job_id_id=response_id, defaults=questionnaire_data)
            if 'advertise_company_details' in data:
                advertise_data = {"advertise_company_details_id_id":data["advertise_company_details"]["key"],"job_id_id":response_id}
                AdvertiseCompanyDetailsJobMapping.objects.update_or_create(job_id_id=response_id, defaults=advertise_data)
            if 'publish_job' in data:
                PostJobs.objects.filter(id=response_id).update(**{"schedule_time": data["publish_job"]["refresh_time"],
                                                                  "status": data["publish_job"]["job_type"],
                                                                  "from_count": 5})
            return Response({"status": True, "message": Message["EMPLOYER_POST_JOBS"]["POST_JOBS_SUCCESS"], "id": response_id}, status=200)
        except Exception as e:
            return Response({"status": False, "message": format(e)}, status=200)


# This function used to get Adertise details from database
# for every user only single details of get adverise
class GetAdvertise(APIView):
    @permission_required()
    def get(self, request):
        try:
            user_id, user_type = request.META["user_id"], request.META["user_type"]
            if "key" not in request.GET:
                return Response({"status": True, "message": Message["EMPLOYER_POST_JOBS"]["GET_ADVERTISE_ERROR"]}, status=200)
            key, advertise_object = request.GET["key"], []
            queryset = AdvertiseCompanyDetailsUserMapping.objects.filter(user_account_id=user_id)
            serializers_advertise = AdvertiseCompanyDetailsUserMappingSerialiser(queryset, many=True).data
            for data in serializers_advertise:
                if int(key) is data["advertise_company_details_id"]["id"]:
                    object = {"key": data["advertise_company_details_id"]["id"],
                              "description": data["advertise_company_details_id"]["organisation_description"],
                              "url": data["advertise_company_details_id"]["website_url"],
                              "address": data["advertise_company_details_id"]["address"],
                              "number": data["advertise_company_details_id"]["contact_number"],
                              "file_url":"",
                              "organisation_name": data["advertise_company_details_id"]["organisation_name"]["name"],
                              "contact_person": data["advertise_company_details_id"]["contact_person"]
                              }
                    if data["advertise_company_details_id"]["file_path"] is not None:
                        object["file_url"] = server_settings["base_url"] + data["advertise_company_details_id"]["file_path"]
                    advertise_object.append(object)
            return Response({"status": True, "message": Message["EMPLOYER_POST_JOBS"]["GET_ADVERTISE_SUCCESS"], "data": advertise_object}, status=200)
        except Exception as e:
            return Response({"status": False, "message": format(e)}, status=200)


# This function used to get Adertise details from database
# for every user only single details of get adverise
class SearchAdvertise(APIView):
    @permission_required()
    def get(self, request):
        try:
            user_id, user_type = request.META["user_id"], request.META["user_type"]
            advertise_object =[]
            search = request.GET["search"] if 'search' in request.GET else ""
            queryset = AdvertiseCompanyDetailsUserMapping.objects.filter(user_account_id=user_id)
            serializers_advertise = AdvertiseCompanyDetailsUserMappingSerialiser(queryset, many=True).data
            for data in serializers_advertise:
                if search in data["advertise_company_details_id"]["organisation_name"]["name"]:
                    object = {"key": data["advertise_company_details_id"]["id"],
                              "description": data["advertise_company_details_id"]["organisation_description"],
                              "url": data["advertise_company_details_id"]["website_url"],
                              "address": data["advertise_company_details_id"]["address"],
                              "number": data["advertise_company_details_id"]["contact_number"],
                              "file_url":"",
                              "organisation_name": data["advertise_company_details_id"]["organisation_name"]["name"],
                              "contact_person": data["advertise_company_details_id"]["contact_person"]
                              }
                    if data["advertise_company_details_id"]["file_path"] is not None:
                        object["file_url"] = server_settings["base_url"] + data["advertise_company_details_id"]["file_path"]
                    advertise_object.append(object)
            return Response({"status": True, "message": Message["EMPLOYER_POST_JOBS"]["SEARCH_ADVERTISE_SUCCESS"], "data": advertise_object}, status=200)
        except Exception as e:
            return Response({"status": False, "message": format(e)}, status=200)


# This function used to delete Adertise details from database
class DeleteAdvertise(APIView):
    @permission_required()
    def get(self, request):
        try:
            user_id, user_type = request.META["user_id"], request.META["user_type"]
            if 'key' not in request.GET:
                return Response({"status": True, "message": Message["EMPLOYER_POST_JOBS"]["DELETE_ADVERTISE_ERROR"]}, status=200)
            AdvertiseCompanyDetails.objects.filter(id=request.GET["key"]).delete()
            return Response({"status": True, "message": Message["EMPLOYER_POST_JOBS"]["DELETE_ADVERTISE_SUCCESS"]}, status=200)
        except Exception as e:
            return Response({"status": False, "message": format(e)}, status=200)


# This function used to create new advetise details in database using user id
# This will save document also in database
class CreateAdvertise(APIView):
    @permission_required()
    def post(self, request):
        try:
            user_id, user_type = request.META["user_id"], request.META["user_type"]
            req = request.data
            data = {"address": req["address"], "website_url": req["url"], "contact_number": req["number"],
                    "organisation_description": req["description"], "contact_person": req["contact_person"]}
            if type(req["number"]) is not int and req["number"] is not "":
                return Response({"status": False, "message": Message["EMPLOYER_POST_JOBS"]["CREATE_ADVERTISE_ERROR"]}, status=200)
            if type(req["organisation_name"]) is int:
                data["organisation_name_id"] = req["organisation_name"]
            else:
                data["organisation_name_id"] = update_new_values(Organizations, req["organisation_name"], "name")
            if req["document"] is not "":
                if validate_file_size(req["document"], 1024 * 1024 * 2):
                    return Response({"status": True, "message": Message["UPDATE_PROFILE_EXCEED_FILE_SIZE"]}, status=200)
                data["file_path"] = req["document"]
            advertise = AdvertiseCompanyDetails.objects.create(**data)
            AdvertiseCompanyDetailsUserMapping.objects.create(**{"advertise_company_details_id_id":advertise.id, "user_account_id_id":user_id})
            return Response({"status": True, "message": Message["EMPLOYER_POST_JOBS"]["CREATE_ADVERTISE_SUCCESS"], "id":advertise.id}, status=200)
        except Exception as e:
            return Response({"status": False, "message": format(e)}, status=200)


# This function used to edit the advertise details
# This function checks every filed is present or not in request data
# and update only those filed having data
class UpdateAdvertise(APIView):
    @permission_required()
    def post(self, request):
        try:
            user_id, user_type = request.META["user_id"], request.META["user_type"]
            req = request.data
            if 'key' not in req or req["key"] is "":
                return Response({"status": True, "message": Message["EMPLOYER_POST_JOBS"]["UPDATE_ADVERTISE_ERROR"]}, status=200)
            advertise_data = AdvertiseCompanyDetails.objects.filter(id=req["key"])
            if advertise_data:
                if req["organisation_name"] is not "":
                    if type(req["organisation_name"]) is int:
                        advertise_data[0].organisation_name_id = req["organisation_name"]
                    else:
                        advertise_data[0].organisation_name_id = update_new_values(Organizations,
                                                                                   req["organisation_name"],
                                                                                   "name")
                if req["address"] is not "":
                    advertise_data[0].address = req["address"]
                if req["description"] is not "":
                    advertise_data[0].organisation_description = req["description"]
                if type(req["number"]) is int and req["number"] is not "":
                    advertise_data[0].contact_number = req["number"]
                if req["document"] is not "":
                    if validate_file_size(req["document"], 1024 * 1024 * 2):
                        return Response({"status": True, "message": Message["UPDATE_PROFILE_EXCEED_FILE_SIZE"]},status=200)
                    advertise_data[0].file_path = req["document"]
                if req["contact_person"] is not "":
                    advertise_data[0].contact_person = req["contact_person"]
                if req["url"] is not "":
                    advertise_data[0].website_url = req["url"]
                advertise_data[0].save()
                return Response({"status": True, "message": Message["EMPLOYER_POST_JOBS"]["UPDATE_ADVERTISE_SUCCESS"]}, status=200)
            else:
                return Response({"status": False, "message": Message["EMPLOYER_POST_JOBS"]["UPDATE_ADVERTISE_ERROR"]}, status=200)
        except Exception as e:
            return Response({"status": False, "message": format(e)}, status=200)


# This function used to get Organisations names in advertise my details tab of post jobs
# This function returns key and values means id as key and name as values
class GetOrganizations(APIView):
    @permission_required()
    def get(self, request):
        try:
            if 'search' in request.GET:
                search = request.GET["search"]
            else:
                return Response({"status": False, "message": Message["EMPLOYER_POST_JOBS"]["GET_ORGANISATION_ERROR"]}, status=200)
            queryset_organizations_name = Organizations.objects.filter(Q(name__icontains=search))
            serializer = OrganizationsSerializer(queryset_organizations_name, many=True).data
            return Response({"status":True, "message": Message["EMPLOYER_POST_JOBS"]["GET_ORGANISATION_SUCCESS"],
                             "data": serializer}, status=200)
        except Exception as e:
            return Response({"status": False, "message":format(e)}, status=200)


# This function used to create new entry in databased for some drop down details like skill
# After that it will return  id to send respected filled
def update_new_values(table_name, value, field_name):
    if type(value) is int:
        return value
    if value is "":
        return value
    print("+++++++++++", value, "++++++++++++++")
    search_type = '__icontains'
    field_nm = field_name + search_type
    info = table_name.objects.filter(**{field_nm: value})
    if info:
        return info[0].id
    else:
        new_value = table_name.objects.create(**{field_name:value})
        return new_value.id


# This function used to excecute raw query in database
# So we have just send query and it will return probable result
def raw_query_execute_function(query):
    cursor = connection.cursor()
    cursor.execute(query)
    return cursor.fetchall()
