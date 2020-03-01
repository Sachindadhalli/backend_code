from .homepage_models import *
from job_seeker.models import OTPVerification
from pinkjob.utils import *
import time
from employer.decorators import *


def update_new_values_homepage(table_name, value, field_name):
    if type(value) is int:
        return value
    search_type = '__icontains'
    field_nm = field_name + search_type
    info = table_name.objects.filter(**{field_nm: value})
    if info:
        return info[0].id
    else:
        new_value = table_name.objects.create(**{field_name: value})
        return new_value.id


def otp_validation(request, status):
    user_id, user_type = request.META["user_id"], request.META["user_type"]
    otp_details = OTPVerification.objects.filter(verification_type="email_id",
                                                 verification_id=request.GET["email_id"],
                                                 otp_status="N").order_by("-id")
    if otp_details and str(otp_details[0].otp) == str(request.GET["otp"]):
        if int(time.time() * 1000) - (120 * 60 * 1000) <= int(otp_details[0].timestamp):
            otp_details[0].otp_status = "V"
            otp_details[0].save()
            if status == "contact_details":
                EmployerProfile.objects.update_or_create(
                    user_account_id=user_id,
                    defaults={
                        "user_account_id_id": user_id,
                        "business_email": request.GET["email_id"],
                        "is_business_email_verified": True
                    })
            else:
                UserAccount.objects.update_or_create(
                    user_account_id=user_id,
                    defaults={
                        "user_account_id_id": user_id,
                        "email_id": request.GET["email_id"],
                        "is_business_email_verified": True
                    })
            return True, Message["EMPLOYER_HOMEPAGE"]["EMAIL_OTP_SUCCESS"]
        else:
            otp_details[0].otp_status = "E"
            otp_details[0].save()
            return False, Message["EMPLOYER_HOMEPAGE"]["EMAIL_OTP_EXPIRE"]
    else:
        return False, Message["EMPLOYER_HOMEPAGE"]["OTP_IS_WRONG"]
