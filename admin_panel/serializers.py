from rest_framework import serializers
from accounts.models import User
from loans.models import Loan
from mpesa.models import MpesaTransaction
from .models import AdminActionLog

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'is_active', 'is_staff',
            'date_joined', 'last_login', 'wallet_frozen'
        ]


class LoanSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField()

    class Meta:
        model = Loan
        fields = [
            'id', 'user', 'amount', 'status', 'created_at', 'updated_at'
        ]


class TransactionSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField()

    class Meta:
        model = MpesaTransaction
        fields = [
            'id', 'user', 'phone_number', 'amount', 'reference',
            'status', 'timestamp'
        ]


class AdminActionLogSerializer(serializers.ModelSerializer):
    admin_user = serializers.StringRelatedField()
    target_user = serializers.StringRelatedField()
    loan = serializers.StringRelatedField()

    class Meta:
        model = AdminActionLog
        fields = [
            'id', 'admin_user', 'action', 'target_user', 'loan',
            'notes', 'timestamp'
        ]
