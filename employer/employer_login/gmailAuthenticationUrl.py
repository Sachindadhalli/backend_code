## This is gmail authentication login api used for gmail login
## first api is called when user click on login with gmail
## second api called when gmail redirect user credentials  

from django.conf.urls import url
from django.urls import path
from . import gmailAuthentication

urlpatterns = [
    url(r'^gmailAuthenticate', gmailAuthentication.gmail_authenticate, name='gmail_authenticate'),
    url(r'^oauth2callback', gmailAuthentication.auth_return)
]
