from django.urls import path,include
from .login_views import *
# from .gmailAuthentication import *
urlpatterns = [
    path('login/',Login.as_view()),
    path('fb-login/',FBLogin.as_view()),
    path('gmail-login/',GmailLogin.as_view()),
    path('linkedin-login',LinkedinLogin.as_view()),
    path('forgot-password/',ForgotPassword.as_view()),
    path('linkedin-callback/',LinkedinCallback.as_view()),
    path('linkedin-user-tokens/',LinkedinUserTokens.as_view()),
    path('new-password/',NewPassword.as_view()),
    path('otp-validate/',OTPValidate.as_view()),
    # path('gmailAuthenticate',GmailAuthenticate.as_view()),
    # path('oauth2callback',Oauth2Callback.as_view())
]
