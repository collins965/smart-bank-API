from rest_framework import generics, permissions
from accounts.models import User
from loans.models import Loan
from mpesa.models import MpesaTransaction
from .serializers import UserSerializer, LoanSerializer, TransactionSerializer


class AdminUserList(generics.ListAPIView):
    """
    Admin-only endpoint to list all registered users.
    """
    permission_classes = [permissions.IsAdminUser]
    queryset = User.objects.all()
    serializer_class = UserSerializer


class AdminLoanList(generics.ListAPIView):
    """
    Admin-only endpoint to list all loan applications.
    """
    permission_classes = [permissions.IsAdminUser]
    queryset = Loan.objects.all()
    serializer_class = LoanSerializer


class AdminTransactionList(generics.ListAPIView):
    """
    Admin-only endpoint to list all M-Pesa transactions.
    """
    permission_classes = [permissions.IsAdminUser]
    queryset = MpesaTransaction.objects.all()
    serializer_class = TransactionSerializer
