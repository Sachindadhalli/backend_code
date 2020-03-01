# This file contains urls for Job seeker Login.
# The followings are child urls for base url(/job-seeker-login/)
# by using following url path the specified functions are runs. 

from django.urls import path,include
from .views import *

# this are all /job-seeker-login/ api listed here with function name
urlpatterns = [
    path('login/', Login.as_view()),
    path('forgot-password/', ForgotPassword.as_view()),
    path('new-password/', ChangePassword.as_view()),
    path('otp-validate/', OTPValidate.as_view()),
    
]
