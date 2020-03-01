from django.urls import path
from .account_settings_views import *

urlpatterns = [
    path('get-email/', SendUserEmail.as_view()),
    path('change-email/', ChangeUserEmail.as_view()),
    path('change-password/', ChangeUserPassword.as_view()),
    path('alter-account/', AlterUserAccount.as_view()),
    path('get-subuserlist/', GetSubUserList.as_view()),
    path('alter-subuser/', AlterSubUser.as_view())
]
