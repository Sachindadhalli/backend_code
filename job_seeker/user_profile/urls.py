# This file contains urls for Job seeker registration.
# The followings are child urls for base url(/job-seeker-registration/)
# by using following url path the specified functions are runs. 

from django.urls import path,include
from .view import GetUserDetails
# from .view import UploadPhoto
from .view import ResumeHeadline
# from .view import GetResumeHeadline
# from .view import PostTechnologies
# # from .view import GetTechnologies
# from .view import Employment
# from .view import PostTechnologies_worked
# from .view import GetTechnologies_worked
# from .view import PostProfileSummery
# from .view import GetProfileSummery
# from .view import PostDesiredCareer
# from .view import GetDesiredCareer
# from .view import PostProjectDetails
# from .view import GetProjectDetails
# from .view import PatchProjectDetails


urlpatterns = [
    path('user-details/',GetUserDetails.as_view()),
    # path('user-photo/',UploadPhoto.as_view()),
    path('resumeheadline/',ResumeHeadline.as_view()),
    # path('get-resumeheadline/',GetResumeHeadline.as_view()),
    # path('post-technologies/',PostTechnologies.as_view()),
    # # path('get-technologies/',GetTechnologies.as_view()),
    # path('employment/',Employment.as_view()),
    # path('post-technologies-worked/',PostTechnologies_worked.as_view()),
    # path('get-technologies-worked/',GetTechnologies_worked.as_view()),
    # path('post-profile-summery/',PostProfileSummery.as_view()),
    # path('get-profile-summery/',GetProfileSummery.as_view()),
    # path('post-desired-career/',PostDesiredCareer.as_view()),
    # path('get-desired-career/',GetDesiredCareer.as_view()),
    # path('post-project-details/',PostProjectDetails.as_view()),
    # path('get-project-details/',GetProjectDetails.as_view()),
    # path('patch-project-details/',PatchProjectDetails.as_view()),
]
