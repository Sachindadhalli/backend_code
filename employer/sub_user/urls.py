from django.urls import path
from .views import *

urlpatterns = [
    path('', SubUserView.as_view()),
    path('<int:eid>/', OneSubUserView.as_view()),
    path('permissions/', PermissionsSubUserView.as_view()),
    path('email-permissions/', PermissionsViaEmailSubUserView.as_view()),
    path('demo/', DemoData.as_view())
]
