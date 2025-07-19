from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny # Import AllowAny for registration
from rest_framework import generics, status
from django.contrib.auth.models import User
from django.db import transaction
from django.contrib.auth.hashers import check_password
from django.http import FileResponse
from datetime import datetime

from .models import Wallet, Profile, TransactionHistory
from .serializers import (
    UserSerializer,
    WalletSerializer,
    TransactionHistorySerializer,
)

from .permissions import IsOwnerOrAdmin
from core.pdf_utils import generate_statement_pdf


class UserRegistrationView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [AllowAny] # This is the crucial change to allow unauthenticated registration


class WalletDetailView(generics.RetrieveAPIView):
    serializer_class = WalletSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrAdmin]

    def get_object(self):
        # Ensure the user has a wallet, otherwise it will raise an error
        try:
            return Wallet.objects.get(user=self.request.user)
        except Wallet.DoesNotExist:
            raise status.HTTP_404_NOT_FOUND({"detail": "Wallet not found for this user."})


class SetTransferPinView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        pin = request.data.get('pin')

        if not pin:
            return Response({"detail": "PIN is required."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            profile = request.user.profile
        except Profile.DoesNotExist:
            return Response({"detail": "User profile not found. Please ensure a profile exists for the user."}, status=status.HTTP_404_NOT_FOUND)

        profile.set_transfer_pin(pin)

        return Response({"detail": "Transfer PIN set successfully."}, status=status.HTTP_200_OK)


class MakeTransferView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        sender = request.user
        receiver_username = request.data.get("receiver_username")
        amount = request.data.get("amount")
        pin = request.data.get("pin")

        # Validate all required fields are present
        if not all([receiver_username, amount, pin]):
            return Response({"detail": "Missing required fields (receiver_username, amount, pin)."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            receiver = User.objects.get(username=receiver_username)
            amount = float(amount)
            if amount <= 0:
                return Response({"detail": "Amount must be positive."}, status=status.HTTP_400_BAD_REQUEST)
        except User.DoesNotExist:
            return Response({"detail": "Receiver user not found."}, status=status.HTTP_404_NOT_FOUND)
        except ValueError:
            return Response({"detail": "Invalid amount format."}, status=status.HTTP_400_BAD_REQUEST)

        # Prevent transfer to self
        if sender == receiver:
            return Response({"detail": "Cannot transfer money to yourself."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            sender_profile = Profile.objects.get(user=sender)
        except Profile.DoesNotExist:
            return Response({"detail": "Sender profile not found. Please ensure your profile exists and is complete."}, status=status.HTTP_404_NOT_FOUND)

        # Check transfer PIN
        if not sender_profile.check_transfer_pin(pin):
            return Response({"detail": "Invalid PIN."}, status=status.HTTP_403_FORBIDDEN)

        try:
            with transaction.atomic():
                # Lock wallets for atomic update to prevent race conditions
                sender_wallet = Wallet.objects.select_for_update().get(user=sender)
                receiver_wallet = Wallet.objects.select_for_update().get(user=receiver)

                if sender_wallet.balance < amount:
                    return Response({"detail": "Insufficient balance."}, status=status.HTTP_400_BAD_REQUEST)

                # Perform the transfer
                sender_wallet.balance -= amount
                receiver_wallet.balance += amount
                sender_wallet.save()
                receiver_wallet.save()

                # Record transaction for sender
                TransactionHistory.objects.create(
                    user=sender,
                    sender=sender,
                    receiver=receiver,
                    amount=amount,
                    transaction_type="transfer",
                    status="completed",
                    description=f"Transfer to {receiver.username}"
                )

                # Record transaction for receiver
                TransactionHistory.objects.create(
                    user=receiver,
                    sender=sender,
                    receiver=receiver,
                    amount=amount,
                    transaction_type="transfer",
                    status="completed",
                    description=f"Received from {sender.username}"
                )

        except Wallet.DoesNotExist:
            return Response({"detail": "Sender or receiver wallet not found."}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            # Log the specific error for debugging on the server side
            print(f"Transfer failed due to: {e}")
            return Response({"detail": "Transfer failed due to an internal error."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response({"detail": "Transfer successful."}, status=status.HTTP_200_OK)


class TransactionHistoryListView(generics.ListAPIView):
    serializer_class = TransactionHistorySerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        queryset = TransactionHistory.objects.filter(user=user).order_by('-timestamp')

        # Apply filters from query parameters
        transaction_type = self.request.query_params.get('type')
        min_amount = self.request.query_params.get('min_amount')
        max_amount = self.request.query_params.get('max_amount')
        start_date = self.request.query_params.get('start_date')
        end_date = self.request.query_params.get('end_date')

        if transaction_type:
            queryset = queryset.filter(transaction_type=transaction_type)
        if min_amount:
            try:
                min_amount = float(min_amount)
                queryset = queryset.filter(amount__gte=min_amount)
            except ValueError:
                # Handle invalid min_amount gracefully, though ListAPIView might not directly return this to user
                pass
        if max_amount:
            try:
                max_amount = float(max_amount)
                queryset = queryset.filter(amount__lte=max_amount)
            except ValueError:
                # Handle invalid max_amount gracefully
                pass
        if start_date:
            queryset = queryset.filter(timestamp__date__gte=start_date)
        if end_date:
            queryset = queryset.filter(timestamp__date__lte=end_date)

        return queryset


class WalletTopUpView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        amount = request.data.get("amount")
        try:
            amount = float(amount)
            if amount <= 0:
                return Response({"detail": "Amount must be positive."}, status=status.HTTP_400_BAD_REQUEST)
        except (TypeError, ValueError):
            return Response({"detail": "Invalid amount format."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            wallet = Wallet.objects.get(user=request.user)
        except Wallet.DoesNotExist:
            return Response({"detail": "Wallet not found for this user."}, status=status.HTTP_404_NOT_FOUND)

        wallet.balance += amount
        wallet.save()

        TransactionHistory.objects.create(
            user=request.user,
            sender=request.user, # For top-up, sender is the user themselves
            receiver=request.user, # For top-up, receiver is the user themselves
            amount=amount,
            transaction_type="top_up",
            status="completed",
            description="Wallet top-up"
        )

        return Response({"detail": "Wallet topped up successfully."}, status=status.HTTP_200_OK)


class WalletWithdrawView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        amount = request.data.get("amount")
        try:
            amount = float(amount)
            if amount <= 0:
                return Response({"detail": "Amount must be positive."}, status=status.HTTP_400_BAD_REQUEST)
        except (TypeError, ValueError):
            return Response({"detail": "Invalid amount format."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            wallet = Wallet.objects.get(user=request.user)
        except Wallet.DoesNotExist:
            return Response({"detail": "Wallet not found for this user."}, status=status.HTTP_404_NOT_FOUND)

        if wallet.balance < amount:
            return Response({"detail": "Insufficient balance."}, status=status.HTTP_400_BAD_REQUEST)

        wallet.balance -= amount
        wallet.save()

        TransactionHistory.objects.create(
            user=request.user,
            sender=request.user, # For withdrawal, sender is the user themselves
            receiver=request.user, # For withdrawal, receiver is the user themselves
            amount=amount,
            transaction_type="withdraw",
            status="completed",
            description="Wallet withdrawal"
        )

        return Response({"detail": "Withdrawal successful."}, status=status.HTTP_200_OK)


class TransactionPDFExportView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        month = request.query_params.get('month')
        year = request.query_params.get('year')

        try:
            month = int(month)
            year = int(year)
        except (TypeError, ValueError):
            return Response({"detail": "Invalid 'month' or 'year' format. Please provide integers."}, status=status.HTTP_400_BAD_REQUEST)

        transactions = TransactionHistory.objects.filter(
            user=request.user,
            timestamp__month=month,
            timestamp__year=year
        ).order_by('-timestamp')

        if not transactions.exists():
            return Response({"detail": "No transactions found for the specified month and year."}, status=status.HTTP_404_NOT_FOUND)

        # Assuming generate_statement_pdf returns a BytesIO object
        pdf_buffer = generate_statement_pdf(request.user, transactions, month, year)
        filename = f"statement_{request.user.username}_{month}_{year}.pdf" # More descriptive filename
        return FileResponse(pdf_buffer, as_attachment=True, filename=filename, content_type='application/pdf')
