from .models import *
from rest_framework import serializers


class U_linked_Serializer(serializers.ModelSerializer):
    class Meta:
        model = UserLinkedinDetails
        fields = '__all__'

class DummySerializer(serializers.ModelSerializer):
    user_account_id = U_linked_Serializer(many=True)
    class Meta:
       model = UserAccount
       fields = '__all__'


class EmployerSerializer(serializers.ModelSerializer):
   class Meta:
       model = UserAccount
       fields = '__all__'

class SignUpSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserAccount
        fields = ('email_id', 'password', 'is_employer')
        extra_kwargs = {'password': {'write_only': True, 'required': True}}
