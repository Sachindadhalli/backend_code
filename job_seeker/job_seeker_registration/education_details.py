# This file contains Education details page API's for Job seeker registration. 
#The apis are get Qualification, get Majors, get University, and Get institute. 

from rest_framework.views import APIView
from rest_framework.response import Response
from pinkjob.utils import *
from job_seeker.serializers import *
from job_seeker.models import *
from job_seeker.services import *
from .views import *


##This is a get Qualification api which will send back all qualification from the database.
class GetQualifications(APIView):
    def get(self, request):
        try:
            queryset_educationQualification = EducationalQualifications.objects.filter()
            serializer = EducationalQualificationsSerializer(queryset_educationQualification, many=True).data
            return Response({"status":True, "message":Message["JOB_SEEKER_REGISTRATION"]["GET_QUALIFICATION_SUCCESS"],"data":serializer},status=200)
        except Exception as e:
            return Response({"status": False, "message":format(e)}, status=200)


##This is Get Major api which content two different structure depend on qualification id
##if qualification id is belong to 10th/ 12th then result will be board name and medium name
##If qualification id is belong to greater than 12th qualification then result will be majors name and specialization of that qualification
class GetMajors(APIView):
    def get(self, request):
        try:
            if 'key' in request.GET:
                id = request.GET["key"]
                queryset_qualification = EducationalQualifications.objects.get(id=id)
                qualification = queryset_qualification.qualification_name
            else:
                return Response({"status": False, "message":Message["JOB_SEEKER_REGISTRATION"]["GET_MAJORS_ERROR"]}, status=200)
            if qualification == "10th" or qualification =="12th":
                serializerBoard = BoardSerializer(Boards.objects.all(), many=True).data
                serializerMedium = MediumSerializer(Medium.objects.all(), many=True).data
                BoardList, MediumList = [], [] 
                for data in serializerBoard:
                    BoardList.append({"key":data["id"],"value":data["board_name"]}) 
                for data in serializerMedium:
                    MediumList.append({"key":data["id"],"value":data["medium_name"]}) 
                return Response({"status":True,"message":Message["JOB_SEEKER_REGISTRATION"]["GET_MAJORS_SUCCESS"], "data":{"board":BoardList,"medium":MediumList}},status=200)
            elif qualification=="Below 10th":
                return Response({"status":True,"message":Message["JOB_SEEKER_REGISTRATION"]["GET_MAJORS_SUCCESS"], "data":{}},status=200)              
            else:
                serializer_major= MajorsSerializer(Majors.objects.filter(qualification_id=id), many=True).data
                structure = []
                for data in serializer_major:
                    spec=[]
                    queryset_specification = Specializations.objects.filter(majors_id=data["id"])
                    serializer_specification= SpecializationsSerializer(queryset_specification, many=True).data
                    for i in serializer_specification:
                        print(i["specialization_name"])
                        spec.append({"key":i["id"],"value":i["specialization_name"]})
                    structure.append({"key":data["id"],"value":data["major_name"],"specialization":spec})
                return Response({"status":True,"message":Message["JOB_SEEKER_REGISTRATION"]["GET_MAJORS_SUCCESS"], "data":structure},status=200)
        except Exception as e:
            return Response({"status": False, "message":format(e)}, status=200)

##This is a get university api which will give all universities from the database
class GetUniversity(APIView):
    def get(self, request):
        try:
            queryset_university = Universities.objects.filter()
            serializer_university = UniversitySerializer(queryset_university, many=True).data
            return Response({"status":True, "message":Message["JOB_SEEKER_REGISTRATION"]["GET_UNIVERSITY_SUCCESS"],"data":serializer_university},status=200)
        except Exception as e:
            return Response({"status": False, "message":format(e)}, status=200)

##This is get institue api which will give institites depends on university id
class GetInstitute(APIView):
    def get(self,request):
        try:
            if 'key' in request.GET:
                id = request.GET["key"]
            else:
                return Response({"status": False, "message":Message["JOB_SEEKER_REGISTRATION"]["GET_INSTITUTES_ERROR"]}, status=200)
            university = UniversitiesInstitutesMapping.objects.filter(university_id=id)
            university = university.prefetch_related("institute_id")
            serializer_institutes = UIMappingSerializer(university, many=True).data
            institute = []
            for data in serializer_institutes:
                institute.append({"key":data["id"],"value":data["institute_id"]["institute_name"]})
            return Response({"status":True, "message":Message["JOB_SEEKER_REGISTRATION"]["GET_INSTITUTES_SUCCESS"],"data":institute},status=200)
        except Exception as e:
            return Response({"status": False, "message":format(e)}, status=200)


##This is get institue api which will give institites depends on university id
class GetSkillSet(APIView):
    def get(self,request):
        try:
            if 'search' in request.GET:
                id = request.GET["search"]
            else:
                return Response({"status": False, "message":Message["JOB_SEEKER_REGISTRATION"]["GET_SKILL_SET_ERROR"]}, status=200)
            skill_set = SkillSet.objects.filter(skill_set_name__icontains=id)
            serializer_skill_set = SkillSetSerializer(skill_set, many=True).data
            return Response({"status":True, "message":Message["JOB_SEEKER_REGISTRATION"]["GET_SKILL_SET_SUCCESS"],"data":serializer_skill_set},status=200)
        except Exception as e:
            return Response({"status": False, "message":format(e)}, status=200)

# this api use to get grading system from database
# this will send grading syatem with id 
class GetGradingSystem(APIView):
    def get(self,request):
        try:
            grading_system = GradingSystem.objects.all()
            serializer_grading_system = GradingSystemSerializer(grading_system, many=True).data
            return Response({"status":True, "message":Message["JOB_SEEKER_REGISTRATION"]["GET_SKILL_SET_SUCCESS"],"data":serializer_grading_system},status=200)
        except Exception as e:
            return Response({"status": False, "message":format(e)}, status=200)

