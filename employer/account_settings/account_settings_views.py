from rest_framework.views import APIView
from rest_framework.response import Response
from employer.decorators import permission_required
from .account_settings_serializers import *
from django.db.models import Q
from django.db import connection
from pinkjob.utils import *
from employer.employer_homepage.homepage_models import *
import time


# This function will send the user's Email ID initially
class SendUserEmail(APIView):
	@permission_required()
	def get(self, request):
		status, message = False, ""
		try:
			user_id, user_type = request.META["user_id"], request.META["user_type"]
			query_set = UserAccount.objects.filter(id=user_id)
			serializer = GetEmailSerializer(query_set, many=True).data
			if len(serializer) == 1:
				status, message = True, serializer[0]['email_id']
			else:
				message = Message["ACCOUNT_SETTINGS"]["USER_COUNT_CONFLICT"]
		except Exception as e:
			message = format(e)
		finally:
			return Response({"status": status, "message": message}, status=200)


# This function allows to edit user's Email ID
class ChangeUserEmail(APIView):
	@permission_required()
	def post(self, request):
		status, message = False, ""
		try:
			user_id, user_type = request.META["user_id"], request.META["user_type"]
			data = request.data
			if (data is []) or (not all(k in data for k in ("new_email", "password"))):
				message = Message["ACCOUNT_SETTINGS"]["INVALID_REQUEST"]
			else:
				new_email = data['new_email']
				pwd = data['password']
				validity = email_length_check(new_email)
				if validity['result']:
					query_set = UserAccount.objects.filter(Q(id=user_id) & Q(password=pwd))
					if len(query_set) == 1:
						existence = UserAccount.objects.filter(Q(email_id=new_email) & Q(is_employer=True)).exists()
						if existence:
							message = Message["EMAIL_IS_REGISTER_WITH_US"]
						else:
							query_set[0].email_id = new_email
							query_set[0].save()
							status, message = True, Message["ACCOUNT_SETTINGS"]["EMAIL_CHANGE_SUCCESS"]
					else:
						message = Message["ACCOUNT_SETTINGS"]["PASSWORD_INCORRECT"]
				else:
					message = validity['message']
		except Exception as e:
			message = format(e)
		finally:
			return Response({"status": status, "message": message}, status=200)


# This function allows to edit user's Password
class ChangeUserPassword(APIView):
	@permission_required()
	def post(self, request):
		status, message = False, ""
		try:
			user_id, user_type = request.META["user_id"], request.META["user_type"]
			data = request.data
			if (data is []) or (not all(key in data for key in ('old_pwd', 'new_pwd', 'conf_pwd'))):
				message = Message["ACCOUNT_SETTINGS"]["INVALID_REQUEST"]
			else:
				old_pwd, new_pwd, conf_pwd = data['old_pwd'], data['new_pwd'], data['conf_pwd']
				if old_pwd == "":
					message = Message["ACCOUNT_SETTINGS"]["EMPTY_CURRENT_PASSWORD"]
				elif new_pwd == "":
					message = Message["ACCOUNT_SETTINGS"]["EMPTY_NEW_PASSWORD"]
				elif conf_pwd == "":
					message = Message["ACCOUNT_SETTINGS"]["EMPTY_CONFIRM_PASSWORD"]
				elif new_pwd != conf_pwd:
					message = Message["ACCOUNT_SETTINGS"]["REENTERED_PASSWORD_MISMATCH"]
				elif old_pwd == new_pwd:
					message = Message["ACCOUNT_SETTINGS"]["PASSWORD_REUSE_ERROR"]
				elif is_password_valid(new_pwd):
					query_set = UserAccount.objects.filter(id=user_id)
					if len(query_set) != 1:
						message = Message["ACCOUNT_SETTINGS"]["USER_COUNT_CONFLICT"]
					else:
						if query_set[0].password != old_pwd:
							message = Message["ACCOUNT_SETTINGS"]["PASSWORD_INCORRECT"]
						else:
							query_set[0].password = new_pwd
							query_set[0].save()
							status, message = True, Message["ACCOUNT_SETTINGS"]["PASSWORD_CHANGE_SUCCESS"]
				else:
					message = Message["ACCOUNT_SETTINGS"]["PASSWORD_INVALID"]
		except Exception as e:
			message = format(e)
		finally:
			return Response({"status": status, "message": message}, status=200)


# This function allows the user delete his/her own account
class AlterUserAccount(APIView):
	@permission_required()
	def post(self, request):
		status, message, act, reason, time_frame, user_id = False, "", "", "", "", ""
		try:
			user_id, user_type = request.META["user_id"], request.META["user_type"]
			data = request.data
			if (data is []) or (not all(k in data for k in ("action", "reason", "time_frame", "password"))):
				message = Message["ACCOUNT_SETTINGS"]["INVALID_REQUEST"]
			else:
				action, reason, time_frame, pwd = data['action'], data['reason'], data['time_frame'], data['password']
				query_set = UserAccount.objects.filter(Q(id=user_id) & Q(password=pwd))
				if len(query_set) == 1:
					emp_query = EmployerProfile.objects.filter(user_account_id=user_id)
					if len(emp_query) == 1:
						emp_status = emp_query[0].user_status
						if emp_status != "deleted":
							if action == "suspend":
								if emp_status == "suspended":
									message = Message["ACCOUNT_SETTINGS"]["ACCOUNT_SUSPENDED_WARNING"]
								elif time_frame == "":
									message = Message["ACCOUNT_SETTINGS"]["TIME_FRAME_NOT_PROVIDED"]
								else:
									act, status, message = "suspended", True, Message["ACCOUNT_SETTINGS"]["ACCOUNT_SUSPENSION_SUCCESS"]
							elif action == "delete":
								act, status, message = "deleted", True, Message["ACCOUNT_SETTINGS"]["ACCOUNT_DELETION_SUCCESS"]
							elif action == "activate":
								if emp_status == "active":
									message = Message["ACCOUNT_SETTINGS"]["ACCOUNT_ACTIVE_WARNING"]
								else:
									act, status, message = "active", True, Message["ACCOUNT_SETTINGS"]["ACCOUNT_ACTIVATION_SUCCESS"]
							else:
								message = Message["ACCOUNT_SETTINGS"]["INVALID_ACTION_REQUEST"]
						else:
							message = Message["ACCOUNT_SETTINGS"]["ACCOUNT_DELETED_WARNING"]
					else:
						message = Message["ACCOUNT_SETTINGS"]["USER_COUNT_CONFLICT"]
				else:
					message = Message["ACCOUNT_SETTINGS"]["PASSWORD_INCORRECT"]
		except Exception as e:
			message = format(e)
		finally:
			if act == "":
				emp_status_query = EmployerProfile.objects.filter(user_account_id=user_id)
				emp_status_query[0].user_status = act
				emp_status_query[0].reason = reason
				curr_time = int(time.time()) * 1000
				if act == "suspended":
					emp_status_query[0].suspended_date = curr_time
					emp_status_query[0].suspended_till = time_frame
				elif act == "deleted":
					emp_status_query[0].deleted_date = curr_time
				elif act == "active":
					emp_status_query[0].activated_date = curr_time
				emp_status_query[0].save()
			return Response({"status": status, "message": message}, status=200)


# This function returns the list of All Sub-Users as per the status requested
class GetSubUserList(APIView):
	@permission_required()
	def get(self, request):
		status, message, data, count = False, "", [], 0
		try:
			user_id, user_type = request.META["user_id"], request.META["user_type"]
			req = request.GET
			if (req is []) or (not all(k in req for k in ("status", "page", "limit"))):
				message = Message["ACCOUNT_SETTINGS"]["INVALID_REQUEST"]
			else:
				state, page, limit = req["status"], req["page"], req["limit"]
				query_set = EmployerProfile.objects.filter(Q(user_account_id=user_id) & Q(is_sub_user=False))
				if len(query_set) == 1:
					org_id = query_set[0].organization_id
					sub_user_list = EmployerProfile.objects.filter(Q(organization_id=org_id) & Q(is_sub_user=True) & Q(sub_user_status=state))
					serialized_list = ProfileSerializer(sub_user_list, many=True).data
					status, message, data, count = True, Message["ACCOUNT_SETTINGS"]["SUCCESS"], serialized_list[((page - 1) * limit) : ((page * limit) - 1)], len(serialized_list)
				else:
					message = Message["ACCOUNT_SETTINGS"]["UNAUTHORIZED_REQUEST"]
		except Exception as e:
			message = format(e)
		finally:
			return Response({"status": status, "message": message, "data": data, "count": count}, status=200)


# This function is used for altering the status of a Sub-User
class AlterSubUser(APIView):
	@permission_required()
	def post(self, request):
		status, message, act, emp_id, org_id, time_frame, reason = False, "", "", "", "", "", ""
		try:
			user_id, user_type = request.META["user_id"], request.META["user_type"]
			data = request.data
			if (data is []) and (not all(key in data for key in ("action", "emp_id", "time_period", "reason"))):
				message = Message["ACCOUNT_SETTINGS"]["INVALID_REQUEST"]
			else:
				action, emp_id, time_frame, reason = data["action"], data["emp_id"], data["time_period"], data["reason"]
				query_set = EmployerProfile.objects.filter(Q(user_account_id=user_id) & Q(is_sub_user=False))
				if len(query_set) == 1:
					org_id = query_set[0].organization_id
					emp_query = EmployerProfile.objects.filter(Q(user_account_id=emp_id) & Q(organization_id=org_id))
					if len(emp_query) == 1:
						emp_status = emp_query[0].user_status
						if emp_status != "deleted":
							if action == "suspend":
								if emp_status == "suspended":
									message = Message["ACCOUNT_SETTINGS"]["ACCOUNT_SUSPENDED_WARNING"]
								elif time_frame == "":
									message = Message["ACCOUNT_SETTINGS"]["TIME_FRAME_NOT_PROVIDED"]
								else:
									act, status, message = "suspended", True, Message["ACCOUNT_SETTINGS"][
										"ACCOUNT_SUSPENSION_SUCCESS"]
							elif action == "delete":
								act, status, message = "deleted", True, Message["ACCOUNT_SETTINGS"]["ACCOUNT_DELETION_SUCCESS"]
							elif action == "activate":
								if emp_status == "active":
									message = Message["ACCOUNT_SETTINGS"]["ACCOUNT_ACTIVE_WARNING"]
								else:
									act, status, message = "active", True, Message["ACCOUNT_SETTINGS"]["ACCOUNT_ACTIVATION_SUCCESS"]
							else:
								message = Message["ACCOUNT_SETTINGS"]["INVALID_ACTION_REQUEST"]
						else:
							message = Message["ACCOUNT_SETTINGS"]["ACCOUNT_DELETED_WARNING"]
					else:
						message = Message["ACCOUNT_SETTINGS"]["USER_COUNT_CONFLICT"]
				else:
					message = Message["ACCOUNT_SETTINGS"]["UNAUTHORIZED_REQUEST"]
		except Exception as e:
			message = format(e)
		finally:
			if act != "" and status is True:
				emp_status_query = EmployerProfile.objects.filter(Q(user_account_id=emp_id) & Q(organization_id=org_id))
				emp_status_query[0].sub_user_status = act
				emp_status_query[0].reason = reason
				curr_time = int(time.time())*1000
				if act == "suspended":
					emp_status_query[0].suspended_date = curr_time
					emp_status_query[0].suspended_till = time_frame
				elif act == "deleted":
					emp_status_query[0].deleted_date = curr_time
				elif act == "active":
					emp_status_query[0].activated_date = curr_time
					act = "activated"
				emp_status_query[0].save()
				emp_email_query = UserAccount.objects.filter(id=emp_id)
				emp_email = emp_email_query[0].email_id
				emp_name = emp_email_query[0].first_name
				mail_body = "Dear " + emp_name + ", <br><br>Your account at Shenzyn has been " + act + "<br><br>Regards,<br>Shenzyn"
				subject = "Shenzyn Account Notification"
				send_email(subject, mail_body, "gupta@selekt.in", [emp_email])
			return Response({"status": status, "message": message}, status=200)


# This function used to create new entry in databased for some drop down details like skill
# After that it will return  id to send respected filled
def account_settings_update_new_values(table_name, value, field_name):
	if value is int:
		return value
	search_type = '__icontains'
	field_nm = field_name + search_type
	info = table_name.objects.filter(**{field_nm: value})
	if info:
		return info[0].id
	else:
		new_value = table_name.objects.create(**{field_name:value})
		return new_value.id


# This function used to excecute raw query in database
# So we have just send query and it will return probable result
def account_settings_raw_query_execute_function(query):
	cursor = connection.cursor()
	cursor.execute(query)
	return cursor.fetchall()
