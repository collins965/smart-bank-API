from django.db import transaction as db_transaction
from rest_framework import generics, status, serializers
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404

from .models import Profile, Wallet, Transaction
from .serializers import (
    RegisterSerializer,
    ProfileSerializer,
    WalletSerializer,
    TransactionSerializer,
)

#  Register User
class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    permission_classes = [AllowAny]
    serializer_class = RegisterSerializer


#  View Profile
class ProfileDetailView(generics.RetrieveAPIView):
    serializer_class = ProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user.profile


#  Update Profile
class ProfileUpdateView(generics.UpdateAPIView):
    serializer_class = ProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user.profile


#  View Wallet
class WalletDetailView(generics.RetrieveAPIView):
    serializer_class = WalletSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user.wallet


#  View Transaction History
class TransactionListView(generics.ListAPIView):
    serializer_class = TransactionSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        wallet = self.request.user.wallet
        return wallet.sent_transactions.all() | wallet.received_transactions.all()


#  Top-Up / Withdraw
class TransactionCreateView(generics.CreateAPIView):
    serializer_class = TransactionSerializer
    permission_classes = [IsAuthenticated]

    def get_serializer_context(self):
        return {"request": self.request}

    def perform_create(self, serializer):
        wallet = self.request.user.wallet
        amount = serializer.validated_data['amount']
        transaction_type = serializer.validated_data['transaction_type']

        if transaction_type == 'withdraw' and wallet.balance < amount:
            raise serializers.ValidationError("Insufficient balance.")
        if transaction_type == 'top_up':
            wallet.balance += amount
        elif transaction_type == 'withdraw':
            wallet.balance -= amount

        wallet.save()
        serializer.save(wallet=wallet)


#  Set or Update Transfer PIN
class SetTransferPinView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        pin = request.data.get("pin")
        if not pin or len(pin) != 4 or not pin.isdigit():
            return Response({"detail": "PIN must be a 4-digit number."}, status=400)

        request.user.profile.set_transfer_pin(pin)
        return Response({"detail": "Transfer PIN set successfully."}, status=200)


#  Internal Transfer
class TransferView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        sender_wallet = request.user.wallet
        recipient_acc_no = request.data.get("recipient_account")
        amount = request.data.get("amount")
        pin = request.data.get("pin")
        description = request.data.get("description", "")

        if not all([recipient_acc_no, amount, pin]):
            return Response({"detail": "All fields are required."}, status=400)

        try:
            amount = float(amount)
        except ValueError:
            return Response({"detail": "Invalid amount."}, status=400)

        if amount <= 0:
            return Response({"detail": "Amount must be greater than zero."}, status=400)

        if not request.user.profile.check_transfer_pin(pin):
            return Response({"detail": "Invalid transfer PIN."}, status=403)

        try:
            recipient_wallet = Wallet.objects.get(account_number=recipient_acc_no)
        except Wallet.DoesNotExist:
            return Response({"detail": "Recipient account not found."}, status=404)

        if sender_wallet.balance < amount:
            return Response({"detail": "Insufficient balance."}, status=400)

        # Atomic transaction
        with db_transaction.atomic():
            sender_wallet.balance -= amount
            recipient_wallet.balance += amount
            sender_wallet.save()
            recipient_wallet.save()

            Transaction.objects.create(
                sender_wallet=sender_wallet,
                recipient_wallet=recipient_wallet,
                transaction_type="transfer",
                amount=amount,
                description=description,
            )

        return Response({"detail": f"KSh {amount} transferred successfully."}, status=200)
