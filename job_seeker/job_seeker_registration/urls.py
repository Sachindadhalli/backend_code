# This file contains urls for Job seeker registration.
# The followings are child urls for base url(/job-seeker-registration/)
# by using following url path the specified functions are runs. 

from django.urls import path
from .education_details import *
from .work_experience_details import *

urlpatterns = [
    path('email-verification/',EmailVerification.as_view()),
    path('mobile-otp-send/',MobileOTPSend.as_view()),
    path('mobile-otp-verification/',MobileOTPVerification.as_view()),
    path('aadhar-card-verification/',AadharCardVerification.as_view()),
    path('get-qualifications/',GetQualifications.as_view()),
    path('get-majors/',GetMajors.as_view()),
    path('get-university/',GetUniversity.as_view()),
    path('get-institutes/',GetInstitute.as_view()),
    path('get-skill-set/',GetSkillSet.as_view()),
    path('get-grading-system/',GetGradingSystem.as_view()),
    path('get-designation/',GetDesignation.as_view()),
    path('get-company-name/',GetCompanyName.as_view()),
    path('get-city/',GetCity.as_view()),
    path('get-state/',GetState.as_view()),
    path('get-country/',GetCountry.as_view()),
    path('verify-email/',VerifyEmail.as_view()),
    path('register/',Register.as_view()),
    path('store-aadhar/', StoreAadharCard.as_view()),
    path('<int:jid>/document/', DocumentUpload.as_view()),
]
