from rest_framework import serializers
from .models import Investment

class InvestmentSerializer(serializers.ModelSerializer):
    user = serializers.ReadOnlyField(source='user.username') 

    class Meta:
        model = Investment
        fields = [
            'id',
            'user',
            'asset_type',
            'symbol',
            'units',
            'initial_value',
            'current_price',
            'total_value',
            'last_updated',
        ]
        read_only_fields = ['initial_value', 'current_price', 'total_value', 'last_updated']
