#employer sign in unit test will be done in this file

import json
from django.test import APITestCase
from django.test import TestCase
from django.urls import reverse
from pinkjob.utils import *

class EmployerRegistrationAPIViewTestCase(APITestCase):
    url = reverse("/employer-registration/join_recruiter/")

    email_avail_url = "/employer-registration/email-verification/?email_id=gupta@selekt.in"

    def test_email_id_is_available_for_create_account(self):
        """
        Test to verify that a post call with invalid passwords
        """
        response = self.client.get(self.email_avail_url, user_data)
        self.assertEqual(Message["EMPLOYER_REGISTRATION"]["EMAIL_ID_AVAILABLE_TO_USE"], response.message)
    

    def test_invalid_password(self):
        """
        Test to verify that a post call with invalid passwords
        """
        user_data = {
            "email_id": "test@selekt.in",
            "password": "test"
        }
        response = self.client.post(self.url, user_data)
        self.assertEqual(Message["JOB_SEEKER_LOGIN"]["PASSWORD_IS_NOT_MATCHING_STANDARDS"], response.message)
    
    def test_invalid_email_id(self):
        """
        Test to verify that a post call with invalid email id
        """
        user_data = {
            "email_id": "test@selekt.i",
            "password": "test@123"
        }
        response = self.client.post(self.url, user_data)
        self.assertEqual(Message["EMPLOYER_REGISTRATION"]["EMAIL_ID_IS_INVALID"], response.message)

    def test_user_registration(self):
        """
        Test to verify that a post call with user valid data
        """
        user_data = {
            "email_id": "test@selekt.in",
            "password": "test@123"
        }
        response = self.client.post(self.url, user_data)
        self.assertEqual(200, response.status_code)

    def test_unique_email_id_validation(self):
        """
        Test to verify that a post call with already exists email id 
        """
        user_data_1 = {
            "email_id": "test@selekt.in",
            "password": "test@456",
        }
        response = self.client.post(self.url, user_data_1)
        self.assertEqual(Message["EMPLOYER_REGISTRATION"]["EMAIL_ID_ALREADY_REGISTERED"], response.messgae)




class EmployerLoginAPIViewTestCase(APITestCase):
    url = reverse("employer:login")

    def setUp(self):
        self.email_id = "test@selekt.in"
        self.password = "test@123"
        self.is_employer = 1
        self.is_email_verified = 0
        #self.user = User.objects.create_user(self.email, self.password)

    def test_authentication_without_password(self):
        response = self.client.post(self.url, {"email_id": self.email_id})
        self.assertEqual(Message["EMPLOYER_LOGIN"]["LOGIN_FIELDS_MISSING"], response.message)
    
    def test_authentication_without_email_id(self):
        response = self.client.post(self.url, {"password": self.password })
        self.assertEqual(Message["EMPLOYER_LOGIN"]["LOGIN_FIELDS_MISSING"], response.message)

    def test_authentication_with_wrong_password(self):
        response = self.client.post(self.url, {"email_id": self.email_id, "password": "test@1"})
        self.assertEqual(Message["EMPLOYER_LOGIN"]["LOGIN_EMAIL_ID_PASSWORD_WRONG"], response.message)

    def test_authentication_without_login_email_verification(self):
        response = self.client.post(self.url, {"email_id": self.email_id, "password": self.password})
        self.assertEqual(Message["EMPLOYER_LOGIN"]["LOGIN_EMAIL_ID_NOT_VERIFIED"], response.message)
        #self.assertTrue("token" in json.loads(response.data))
    
    # def test_authentication_with_valid_data(self):
    #     response = self.client.post(self.url, {"email_id": "test@selekt.in", "password": self.password})
    #     self.assertEqual(200, response.status_code)
    #     self.assertTrue("auth_token" in json.loads(response.content))

