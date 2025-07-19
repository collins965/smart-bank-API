from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
from django.http import FileResponse

from .models import Profile, Wallet, Transaction, TransactionHistory
from .serializers import (
    RegisterSerializer, ProfileSerializer, WalletSerializer,
    TransactionSerializer, SetTransferPinSerializer,
    TransferSerializer, TransactionHistorySerializer
)
from .utils import generate_statement_pdf

from datetime import datetime


# --- Auth/Register ---
class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]


# --- Profile ---
class ProfileDetailView(generics.RetrieveAPIView):
    serializer_class = ProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user.profile


class ProfileUpdateView(generics.UpdateAPIView):
    serializer_class = ProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user.profile


# --- Wallet ---
class WalletDetailView(generics.RetrieveAPIView):
    serializer_class = WalletSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user.wallet


# --- Transactions ---
class TransactionListView(generics.ListAPIView):
    serializer_class = TransactionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Transaction.objects.filter(user=self.request.user).order_by('-timestamp')


class TransactionCreateView(generics.CreateAPIView):
    serializer_class = TransactionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


# --- Set Transfer PIN ---
class SetTransferPinView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = SetTransferPinSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response({'detail': 'Transfer PIN set successfully.'})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# --- Internal Transfer ---
class TransferView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = TransferSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response({'detail': 'Transfer successful.'})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# --- Transaction History Logs ---
class TransactionHistoryListView(generics.ListAPIView):
    serializer_class = TransactionHistorySerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        queryset = TransactionHistory.objects.filter(user=self.request.user).order_by('-timestamp')

        # Optional filters
        tx_type = self.request.query_params.get('type')
        date = self.request.query_params.get('date')
        amount = self.request.query_params.get('amount')

        if tx_type:
            queryset = queryset.filter(type=tx_type)
        if date:
            queryset = queryset.filter(timestamp__date=date)
        if amount:
            queryset = queryset.filter(amount=amount)

        return queryset


# --- Generate PDF Bank Statement ---
class PDFStatementView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        user = request.user
        month = request.query_params.get('month')
        year = request.query_params.get('year')

        try:
            month = int(month)
            year = int(year)
        except (TypeError, ValueError):
            return Response({'error': 'Month and Year must be provided as integers.'}, status=400)

        transactions = TransactionHistory.objects.filter(
            user=user,
            timestamp__month=month,
            timestamp__year=year
        ).order_by('timestamp')

        if not transactions.exists():
            return Response({'error': 'No transactions found for this period.'}, status=404)

        pdf_buffer = generate_statement_pdf(user, transactions, month, year)
        filename = f"{user.username}_statement_{month}_{year}.pdf"

        return FileResponse(pdf_buffer, as_attachment=True, filename=filename)
