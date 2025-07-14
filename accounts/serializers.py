from rest_framework import serializers
from django.contrib.auth.models import User
from rest_framework.validators import UniqueValidator
from .models import Profile


class ProfileSerializer(serializers.ModelSerializer):
    phone = serializers.CharField(
        required=False,
        allow_blank=True,
        max_length=15
    )
    id_number = serializers.CharField(
        required=False,
        allow_blank=True,
        max_length=20
    )

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
        """
        Create a user along with an optional profile.
        """
        profile_data = validated_data.pop('profile', {})
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password']
        )
        Profile.objects.update_or_create(user=user, defaults=profile_data)
        return user

    def to_representation(self, instance):
        """
        Include profile details in the API response.
        """
        rep = super().to_representation(instance)
        rep['profile'] = ProfileSerializer(instance.profile).data
        return rep
