from django.urls import path,include
from .homepage_views import *

urlpatterns = [
    path('know-about-employer/',KnowAboutEmployer.as_view()),
    path('send-otp/',SendAccountValidateOtp.as_view()),
    path('verify-otp-and-populate-details/',VerifyOTPAndPoputateDetails.as_view()),
    path('get-basic-profile-details/',GetBasicProfileDetails.as_view()),
    path('update-basic-profile-details/',UpdateBasicProfileDetails.as_view()),
    path('get-url-suggestions/',GetUrlSuggestions.as_view()),
    path('customise-url/',CustomiseUrl.as_view()),
    path('update-profile-headline/',ProfileHeadline.as_view()),
    path('get-profile-headline/',GetProfileHeadline.as_view()),
    path('get-industries/',GetIndustries.as_view()),
    path('get-functional-areas/',GetFunctionalAreas.as_view()),
    path('get-levels/',GetLevelIHire.as_view()),
    path('get-contact-details/',GetContactDetails.as_view()),
    path('update-contact-details/',UpdateContactDetails.as_view()),
    path('get-work-experience-details/',GetWorkExperienceDetails.as_view()),
    path('add-work-experience-details/',AddWorkExperienceDetails.as_view()),
    path('update-work-experience-details/',UpdateWorkExperienceDetails.as_view()),
    path('delete-work-experience-details/',DeleteWorkExperienceDetails.as_view()),
    path('upload-documents/',UploadDocuments.as_view()),
    path('get-documents/',GetDocuments.as_view()),
    path('delete-documents/',DeleteDocuments.as_view()),
    path('contact-detail-email-otp/',ContactDetailsEmailOtp.as_view()),
    path('contact-detail-phone-otp/',ContactDetailsPhoneOtp.as_view()),
    path('contact-detail-email-otp-validate/', ContactDetailsEmailOtpValidate.as_view()),
    #path('login-detail-email-otp-validate/', LoginDetailsEmailOtpValidate.as_view()),
    path('contact-detail-phone-otp-validate/',ContactDetailsPhoneOtpValidate.as_view())
]
