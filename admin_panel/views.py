from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAdminUser

from accounts.models import User  # Use your custom User model
from loans.models import Loan
from transactions.models import TransactionHistory  # ✅ Correct model name
from accounts.serializers import UserSerializer
from loans.serializers import LoanSerializer
from transactions.serializers import TransactionSerializer  # Ensure it matches TransactionHistory


class AdminUserList(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        users = User.objects.all()
        serializer = UserSerializer(users, many=True)
        return Response(serializer.data)


class AdminLoanList(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        loans = Loan.objects.all()
        serializer = LoanSerializer(loans, many=True)
        return Response(serializer.data)


class AdminTransactionList(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        transactions = TransactionHistory.objects.all()  # ✅ Correct model usage
        serializer = TransactionSerializer(transactions, many=True)
        return Response(serializer.data)
