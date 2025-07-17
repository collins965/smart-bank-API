from rest_framework import serializers
from accounts.models import User
from loans.models import Loan
from mpesa.models import MpesaTransaction


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'is_active', 'is_staff']


class LoanSerializer(serializers.ModelSerializer):
    class Meta:
        model = Loan
        fields = '__all__'


class TransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = MpesaTransaction
        fields = '__all__'
