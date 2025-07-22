from rest_framework import generics, filters, permissions
from .models import TransactionHistory
from .serializers import TransactionSerializer

class TransactionListView(generics.ListAPIView):
    serializer_class = TransactionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        queryset = TransactionHistory.objects.filter(user=self.request.user)
        transaction_type = self.request.query_params.get('type')
        min_amount = self.request.query_params.get('min_amount')
        max_amount = self.request.query_params.get('max_amount')
        start_date = self.request.query_params.get('start_date')
        end_date = self.request.query_params.get('end_date')

        if transaction_type:
            queryset = queryset.filter(type=transaction_type)
        if min_amount:
            queryset = queryset.filter(amount__gte=min_amount)
        if max_amount:
            queryset = queryset.filter(amount__lte=max_amount)
        if start_date and end_date:
            queryset = queryset.filter(timestamp__range=[start_date, end_date])

        return queryset.order_by('-timestamp')
