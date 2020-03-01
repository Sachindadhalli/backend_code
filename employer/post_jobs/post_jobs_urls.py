from django.urls import path
from .post_jobs_views import *

urlpatterns = [
    path('current-similar-to-previous/', CurrentSimilarToPrevious.as_view()),
    path('get-post-job-details/',PopulateDetails.as_view()),
    path('get-currency/', GetCurrency.as_view()),
    path('get-questionnaire/', GetQuestionnaire.as_view()),
    path('get-questionnaire-names/', GetQuestionnaireNames.as_view()),
    path('create-questionnaire/', CreateQuestionnaire.as_view()),
    path('edit-questionnaire/', EditQuestionnaire.as_view()),
    path('delete-questionnaire/', DeleteQuestionnaire.as_view()),
    path('get-qualifications/', GetQualification.as_view()),
    path('get-phd-qualification/', GetPHDQualification.as_view()),
    path('get-specialisations/', GetSpecializations.as_view()),
    path('get-existing-email/', GetExistingEmail.as_view()),
    path('post-jobs/', PostJob.as_view()),
    path('create-advertise/', CreateAdvertise.as_view()),
    path('get-advertise/', GetAdvertise.as_view()),
    path('search-advertise/', SearchAdvertise.as_view()),
    path('update-advertise/', UpdateAdvertise.as_view()),
    path('delete-advertise/', DeleteAdvertise.as_view()),
    path('get-organisations/', GetOrganizations.as_view())
]


