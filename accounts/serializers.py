from rest_framework import serializers
from django.contrib.auth.models import User
from rest_framework.validators import UniqueValidator
from .models import Profile, Wallet, Transaction


class ProfileSerializer(serializers.ModelSerializer):
    phone = serializers.CharField(required=False, allow_blank=True, max_length=15)
    id_number = serializers.CharField(required=False, allow_blank=True, max_length=20)

    class Meta:
        model = Profile
        fields = ['id_number', 'bio', 'phone', 'date_of_birth', 'address', 'profile_image']


class RegisterSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(
        required=True,
        validators=[UniqueValidator(queryset=User.objects.all())]
    )
    password = serializers.CharField(write_only=True, min_length=6)
    profile = ProfileSerializer(required=False)

    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'profile']

    def create(self, validated_data):
        profile_data = validated_data.pop('profile', {})
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password']
        )
        Profile.objects.update_or_create(user=user, defaults=profile_data)
        return user

    def to_representation(self, instance):
        rep = super().to_representation(instance)
        rep['profile'] = ProfileSerializer(instance.profile).data
        return rep


class WalletSerializer(serializers.ModelSerializer):
    class Meta:
        model = Wallet
        fields = ['account_number', 'balance', 'is_active', 'created_at']
        read_only_fields = fields


class TransactionSerializer(serializers.ModelSerializer):
    transaction_type = serializers.ChoiceField(choices=Transaction.TRANSACTION_TYPES)

    class Meta:
        model = Transaction
        fields = ['id', 'transaction_type', 'amount', 'timestamp', 'description']
        read_only_fields = ['id', 'timestamp']

    def validate_amount(self, value):
        if value <= 0:
            raise serializers.ValidationError("Amount must be greater than 0.")
        return value

    def create(self, validated_data):
        wallet = self.context['request'].user.wallet
        transaction_type = validated_data['transaction_type']
        amount = validated_data['amount']

        # Handle balance logic
        if transaction_type == 'withdraw':
            if wallet.balance < amount:
                raise serializers.ValidationError("Insufficient balance.")
            wallet.balance -= amount
        else:  # top_up
            wallet.balance += amount

        wallet.save()
        return Transaction.objects.create(wallet=wallet, **validated_data)
