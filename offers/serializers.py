# offers/serializers.py

from rest_framework import serializers
from .models import ExclusiveOffer

class ExclusiveOfferSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExclusiveOffer
        fields = '__all__'
