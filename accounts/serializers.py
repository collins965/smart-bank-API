# accounts/serializers.py

from rest_framework import serializers
from django.contrib.auth.models import User
from django.db import transaction
from .models import Profile, Wallet, TransactionHistory


class ProfileSerializer(serializers.ModelSerializer):
    profile_image = serializers.ImageField(required=False, allow_null=True)

    class Meta:
        model = Profile
        fields = [
            "id_number",
            "bio",
            "phone",
            "date_of_birth",
            "address",
            "profile_image",
        ]


class UserSerializer(serializers.ModelSerializer):
    profile = ProfileSerializer()

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'password', 'profile']
        extra_kwargs = {
            'password': {'write_only': True},
            'email': {'required': True}
        }

    def create(self, validated_data):
        profile_data = validated_data.pop('profile')
        password = validated_data.pop('password')

        try:
            with transaction.atomic():
                # Create User
                user = User(**validated_data)
                user.set_password(password)
                user.save()

                # Create or update Profile
                Profile.objects.update_or_create(
                    user=user,
                    defaults={
                        "id_number": profile_data.get("id_number"),
                        "bio": profile_data.get("bio"),
                        "phone": profile_data.get("phone"),
                        "date_of_birth": profile_data.get("date_of_birth"),
                        "address": profile_data.get("address"),
                        "profile_image": profile_data.get("profile_image", None),
                    }
                )

                # Create Wallet if not already created by signals
                Wallet.objects.get_or_create(user=user)

                return user

        except Exception as e:
            raise serializers.ValidationError({
                'error': f'Failed to register user: {str(e)}'
            })


class WalletSerializer(serializers.ModelSerializer):
    class Meta:
        model = Wallet
        fields = ['id', 'balance', 'created_at']


class TransactionHistorySerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField()
    sender = serializers.StringRelatedField()
    receiver = serializers.StringRelatedField()

    class Meta:
        model = TransactionHistory
        fields = [
            'id', 'user', 'sender', 'receiver', 'amount',
            'transaction_type', 'status', 'description', 'timestamp'
        ]
