from employer.employer_homepage.homepage_serializers import *
from rest_framework.views import APIView
from employer.decorators import *
from django.db.models import Q
import datetime


# This function stores the sub-user data
class SubUserView(APIView):
    # make it count or select query
    def count_select_query(self, queryset_main, queryset_1, queryset_2, page, limit, status):
        count = queryset_main.count()
        data = []
        queryset_main = queryset_main[page: page+limit]
        for employer in queryset_main:
            # formatting
            dict = {
                "id": employer.id,
                "name": employer.user_account_id.first_name,
                "email": employer.user_account_id.email_id,
                "designation": employer.designation_id.name,
                "permissions": employer.permissions,
                "added_by": employer.parent_id.first_name
            }
            if status == "suspended":
                dict.update({"suspended_for": str((datetime.datetime.now().date() - employer.suspended_till).days)+" days"})
            elif status == "deleted":
                dict.update(
                    {"reason": employer.reason, "updated_on": time.strftime('%d %b %Y %H:%M%p', time.gmtime(employer.updated_on/1000))})
            data.append(dict)
        queryset_1 = queryset_1.count()
        queryset_2 = queryset_2.count()
        return data, count, queryset_1, queryset_2

    # query for status
    def status_query(self, status, user_id):
        return EmployerProfile.objects.filter(Q(parent_id_id=user_id) & Q(employer_profile_status=status)).order_by(
            "updated_on")

    # queries for active, suspended and deleted
    def querying(self, user_id):
        employer_profile_active = self.status_query("active", user_id)
        employer_profile_suspended = self.status_query("suspended", user_id)
        employer_profile_deleted = self.status_query("deleted", user_id)
        return employer_profile_active, employer_profile_suspended, employer_profile_deleted

    # profile to retrieve sub user
    @permission_required()
    def get(self, request):
        try:
            # for limit of a page
            limit = int(request.GET["limit"])
            # for page number
            page = int(request.GET["page"])
            page -= 1
            page *= limit
            status = request.GET["status"]
            header = {"name": "Name", "email": "Email", "designation": "Role", "permissions": "Permissions"}
            # for active subusers
            if status == "active":
                employer_profile_active, employer_profile_suspended, employer_profile_deleted = self.querying(
                    request.META["user_id"])
                header.update({"added_by": "Added By","actions":"Actions"})
                employer_profile_active, count, employer_profile_suspended, employer_profile_deleted = self.count_select_query(
                    employer_profile_active, employer_profile_suspended, employer_profile_deleted, page, limit, status)
                return Response({"status": True, "message": "sub employer found", "data": employer_profile_active,
                                 "active": count, "suspended": employer_profile_suspended, "header": header,
                                 "deleted": employer_profile_deleted}, status=200)
            elif status == "suspended":
                employer_profile_active, employer_profile_suspended, employer_profile_deleted = self.querying(
                    request.META["user_id"])
                header.update({"suspended_for": "Suspended for","actions":"Actions"})
                employer_profile_suspended, count, employer_profile_active, employer_profile_deleted = self.count_select_query(
                    employer_profile_suspended, employer_profile_active, employer_profile_deleted, page, limit, status)

                return Response({"status": True, "message": "sub employer found", "data": employer_profile_suspended,
                                 "active": employer_profile_active, "suspended": count, "header": header,
                                 "deleted": employer_profile_deleted}, status=200)
            elif status == "deleted":
                employer_profile_active, employer_profile_suspended, employer_profile_deleted = self.querying(
                    request.META["user_id"])
                header.update({"reason": "Reason", "updated_on": "Date & Time of deletion","actions":"Actions"})
                employer_profile_deleted, count, employer_profile_active, employer_profile_suspended = self.count_select_query(
                    employer_profile_deleted, employer_profile_active, employer_profile_suspended, page, limit, status)
                return Response({"status": True, "message": "sub employer found", "data": employer_profile_deleted,
                                 "active": employer_profile_active, "suspended": employer_profile_suspended,
                                 "deleted": count, "header": header}, status=200)
            return Response({"status": True, "message": "Enter Correct Status", "data": [], "header": header}, status=200)

            # data retrieval
        except Exception as e:
            return Response({"status": False, "message": format(e)}, status=200)

    # profile creation of sub user
    @permission_required()
    def post(self, request):
        try:
            data = request.data
            user_id = request.META["user_id"]
            # check account is already there if yes then update if no then create
            user_account = EmployerProfile.objects.filter(Q(business_email=data["email_id"]) & Q(is_business_email_verified=True))
            print(user_account)
            if user_account:
                print(user_account[0].user_account_id_id)
                del data["email_id"]
                #data["parent_id_id "] = user_id;
                EmployerProfile.objects.filter(user_account_id=user_account[0].user_account_id_id).update(
                    is_admin=False,parent_id_id = user_id, updated_on=time.mktime(datetime.datetime.now().timetuple())*1000, **data)
            # else:
            #     user_account = UserAccount.objects.create(
            #         first_name=data["first_name"], email_id=data["email_id"], is_employer=True, is_job_seeker=False,
            #         regestration_date=int(datetime.datetime.now().timestamp()*1000), is_email_verified=False,
            #         is_account_approved=False, is_email_notification_active=False, is_sms_notification_active=False)
            #     del data["email_id"]
            #     EmployerProfile.objects.create(user_account_id=user_account, parent_id_id=user_id, is_sub_user=False,
            #                                    employer_profile_status="active", is_admin=False,
            #                                    created_on=time.mktime(datetime.datetime.now().timetuple())*1000,
            #                                    updated_on=time.mktime(datetime.datetime.now().timetuple())*1000, **data)
            return Response({"status": True, "message": "sub employer updated"}, status=200)
        except Exception as e:
            return Response({"status": False, "message":format(e)}, status=200)


class OneSubUserView(APIView):
    # profile retrieval of sub user
    @permission_required()
    def get(self, request, eid=None):
        try:
            # for reducing queries
            employer_profile = EmployerProfile.objects.filter(id=eid).select_related('designation_id')
            employer_profile = employer_profile.select_related('organization_id')
            employer_profile = employer_profile.select_related('current_country')
            employer_profile = employer_profile.select_related('current_city')
            employer_profile = employer_profile.select_related('user_account_id')
            if not employer_profile:
                return Response({"status": False, "message": "Data Not Found"}, status=200)
            # formatting
            data = {
                "name":  employer_profile[0].user_account_id.first_name,
                "email": employer_profile[0].user_account_id.email_id,
                "designation": employer_profile[0].designation_id.name,
                "permissions": employer_profile[0].permissions}
            return Response({"status": True, "message": "sub employer found", "data": data}, status=200)
        except Exception as e:
            return Response({"status": False, "message": format(e)}, status=200)

    # updation of profile of sub user
    @permission_required()
    def patch(self, request, eid=None):
        try:
            data = request.data
            if "email_id" in data:
                del data["email_id"]
            if "first_name" in data:
                del data["first_name"]
            employer_profile = EmployerProfile.objects.filter(id=eid)
            if employer_profile[0].employer_profile_status != "deleted":
                employer_profile.update(updated_on=time.mktime(datetime.datetime.now().timetuple())*1000, **data)
                return Response({"status": True, "message": "sub employer updated"}, status=200)
            else:
                return Response({"status": True, "message": "sub employer status once deleted can't be updated"},
                                status=200)
        except Exception as e:
            return Response({"status": False, "message": format(e)}, status=200)


class PermissionsSubUserView(APIView):
    # permissions of specific sub user
    @permission_required()
    def get(self, request, eid=None):
        try:
            employer_profile = EmployerProfile.objects.filter(user_account_id_id=request.META["user_id"])
            if employer_profile:
                permissions_object = []
                if employer_profile[0].is_admin:
                    default_permissions = DefaultPermissions.objects.filter()
                    permissions_object = DefaultPermissionsSerializer(default_permissions, many=True).data
                else:
                    if employer_profile[0].permissions:
                        permissions = employer_profile[0].permissions.split(",")
                        for i in permissions:
                            permissions_object.append({"permission_name":i})
                        print(permissions_object)
                    else:
                        permissions_object = []
                return Response({"status": True, "message": "sub employer found", "data": permissions_object}, status=200)
            else:
                return Response({"status": False, "message": "Permissions Not Found"}, status=200)
        except Exception as e:
            return Response({"status": False, "message": format(e)}, status=200)


class PermissionsViaEmailSubUserView(APIView):
    # permissions of specific sub user
    @permission_required()
    def get(self, request, eid=None):
        try:
            business_email_id = request.GET["business_email_id"]
            employer_profile = EmployerProfile.objects.filter(business_email=business_email_id)
            if employer_profile:
                employer_profile = employer_profile.filter(is_business_email_verified=True)
                if employer_profile:
                    permissions = employer_profile[0].permissions
                    first_name = employer_profile[0].user_account_id.first_name
                    last_name = employer_profile[0].user_account_id.last_name
                    designation = employer_profile[0].designation_id.name
                    name = ""
                    if first_name is not None:
                        name = first_name.strip() + " "
                    if last_name is not None:
                        name += last_name.strip() + " "
                    data = {"permissions": permissions, "name": name, "role": designation}
                    return Response({"status": True, "message": "sub employer found", "data": data}, status=200)
                else:
                    return Response({"status": False, "message": "Business Email ID is not verified"}, status=200)
            else:
                return Response({"status": False, "message": "Business Email ID doesn't exist"}, status=200)
        except Exception as e:
            return Response({"status": False, "message": format(e)}, status=200)


class DemoData(APIView):
    # permissions of specific sub user
    #@permission_required()
    def get(self, request, eid=None):
        try:
            for i in range(10):
                user_Account = UserAccount.objects.create(
                    first_name="Test"+str(i), last_name="Last Name"+str(i), email_id="test"+str(i)+"@gmail.com",
                    password="test@123", regestration_date = int(datetime.datetime.now().timestamp()*1000),
                    is_employer=True, is_email_verified=True)
                EmployerProfile.objects.create(
                    user_account_id=user_Account, designation_id_id=1, business_email="testing"+str(i),
                    is_business_email_verified=True, employer_profile_status="active",
                    permissions="Admin,Add Sub User,Post Jobs,Search Resume - Video", is_admin=True)

            for i in range(11, 21):
                user_Account = UserAccount.objects.create(
                    first_name="Test"+str(i), last_name="Last Name"+str(i), email_id="test"+str(i)+"@gmail.com",
                    password="test@123", regestration_date = int(datetime.datetime.now().timestamp()*1000),
                    is_employer=True, is_email_verified=True)
                EmployerProfile.objects.create(
                    user_account_id=user_Account, designation_id_id=1, business_email="testing"+str(i),
                    is_business_email_verified=True, employer_profile_status="suspended",
                    permissions="Admin,Add Sub User,Post Jobs,Search Resume - Video", is_admin=True)

            for i in range(22, 23):
                user_Account = UserAccount.objects.create(
                    first_name="Test"+str(i), last_name="Last Name"+str(i), email_id="test"+str(i)+"@gmail.com",
                    password="test@123", regestration_date = int(datetime.datetime.now().timestamp()*1000),
                    is_employer=True, is_email_verified=True)
                EmployerProfile.objects.create(
                    user_account_id=user_Account, designation_id_id=1, business_email="testing"+str(i),
                    is_business_email_verified=True, employer_profile_status="deleted",
                    permissions="Admin,Add Sub User,Post Jobs,Search Resume - Video", is_admin=True)
            return Response({"status": True, "message": "Data Added"}, status=200)
        except Exception as e:
            return Response({"status": False, "message": format(e)}, status=200)
