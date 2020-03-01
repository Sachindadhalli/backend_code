#All Employer registration urls will be in this file


from django.urls import path,include
from .views import *


urlpatterns = [
    path('email-verification/',EmailVerification.as_view()),
    path('join-recruiter/',JoinRecruiter.as_view()),
    path('verify-email/',VerifyEmail.as_view())
]
