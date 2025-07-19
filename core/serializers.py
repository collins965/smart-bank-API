from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Profile, Wallet, Transaction, TransferPin, TransactionHistory
from django.utils import timezone


# --- User Registration ---
class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)

    class Meta:
        model = User
        fields = ['username', 'email', 'password']

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        Profile.objects.create(user=user)
        Wallet.objects.create(user=user)
        return user


# --- Profile ---
class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ['full_name', 'phone_number', 'address']


# --- Wallet ---
class WalletSerializer(serializers.ModelSerializer):
    class Meta:
        model = Wallet
        fields = ['balance', 'is_frozen']


# --- Transactions ---
class TransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = ['id', 'amount', 'type', 'status', 'timestamp']


class TransactionCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = ['amount', 'type']  # system creates status and timestamp


# --- Transfer PIN ---
class TransferPinSerializer(serializers.Serializer):
    pin = serializers.CharField(min_length=4, max_length=4, write_only=True)


class TransferSerializer(serializers.Serializer):
    recipient_username = serializers.CharField()
    amount = serializers.DecimalField(max_digits=12, decimal_places=2)
    pin = serializers.CharField(min_length=4, max_length=4, write_only=True)


# --- Transaction History ---
class TransactionHistorySerializer(serializers.ModelSerializer):
    sender = serializers.CharField(source='sender.username', read_only=True)
    receiver = serializers.CharField(source='receiver.username', read_only=True)

    class Meta:
        model = TransactionHistory
        fields = ['id', 'sender', 'receiver', 'amount', 'type', 'status', 'timestamp']


# --- Statement Filter Serializer (for PDF generation if needed) ---
class StatementFilterSerializer(serializers.Serializer):
    month = serializers.IntegerField(required=True, min_value=1, max_value=12)
    year = serializers.IntegerField(required=True, min_value=2000, max_value=timezone.now().year)

