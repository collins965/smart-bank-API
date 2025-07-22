from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from django.contrib.auth.models import User
from django.db import transaction, IntegrityError
from django.http import FileResponse

from .models import Wallet, Profile, TransactionHistory
from .serializers import UserSerializer, WalletSerializer, TransactionHistorySerializer
from .permissions import IsOwnerOrAdmin
from core.pdf_utils import generate_statement_pdf


# 🔐 JWT login using username/password
class UsernameTokenObtainPairView(TokenObtainPairView):
    permission_classes = [AllowAny]
    serializer_class = TokenObtainPairSerializer


class UserRegistrationView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        try:
            return super().create(request, *args, **kwargs)
        except IntegrityError as e:
            return Response({"error": f"Integrity error: {str(e)}"}, status=400)
        except Exception as e:
            return Response({"error": f"Unexpected error: {str(e)}"}, status=500)


class WalletDetailView(generics.RetrieveAPIView):
    serializer_class = WalletSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrAdmin]

    def get_object(self):
        wallet, _ = Wallet.objects.get_or_create(user=self.request.user)
        return wallet


class SetTransferPinView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        pin = request.data.get('pin')
        if not pin:
            return Response({"detail": "PIN is required."}, status=400)

        profile, _ = Profile.objects.get_or_create(user=request.user)
        try:
            profile.set_transfer_pin(pin)
            return Response({"detail": "Transfer PIN set successfully."}, status=200)
        except Exception as e:
            return Response({"detail": f"Invalid PIN: {str(e)}"}, status=400)


class MakeTransferView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        sender = request.user
        receiver_username = request.data.get("receiver_username")
        amount = request.data.get("amount")
        pin = request.data.get("pin")

        if not all([receiver_username, amount, pin]):
            return Response({"detail": "Missing required fields."}, status=400)

        try:
            receiver = User.objects.get(username=receiver_username)
            amount = float(amount)
            if amount <= 0:
                return Response({"detail": "Amount must be positive."}, status=400)
        except User.DoesNotExist:
            return Response({"detail": "Receiver not found."}, status=404)
        except ValueError:
            return Response({"detail": "Invalid amount."}, status=400)

        if sender == receiver:
            return Response({"detail": "Cannot transfer to yourself."}, status=400)

        try:
            sender_profile = sender.profile
            if not sender_profile.check_transfer_pin(pin):
                return Response({"detail": "Invalid PIN."}, status=403)
        except Profile.DoesNotExist:
            return Response({"detail": "Sender profile not found."}, status=404)

        try:
            with transaction.atomic():
                sender_wallet = Wallet.objects.select_for_update().get(user=sender)
                receiver_wallet = Wallet.objects.select_for_update().get(user=receiver)

                if not sender_wallet.can_withdraw(amount):
                    return Response({"detail": "Insufficient funds or wallet is frozen."}, status=400)

                sender_wallet.balance -= amount
                receiver_wallet.balance += amount
                sender_wallet.save()
                receiver_wallet.save()

                TransactionHistory.objects.bulk_create([
                    TransactionHistory(
                        user=sender, sender=sender, receiver=receiver,
                        amount=amount, transaction_type="transfer", status="completed",
                        description=f"Transfer to {receiver.username}"
                    ),
                    TransactionHistory(
                        user=receiver, sender=sender, receiver=receiver,
                        amount=amount, transaction_type="transfer", status="completed",
                        description=f"Received from {sender.username}"
                    )
                ])
        except Wallet.DoesNotExist:
            return Response({"detail": "Wallet not found."}, status=404)
        except Exception as e:
            return Response({"detail": f"Internal error: {str(e)}"}, status=500)

        return Response({"detail": "Transfer successful."}, status=200)


class WalletTopUpView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        amount = request.data.get("amount")
        try:
            amount = float(amount)
            if amount <= 0:
                return Response({"detail": "Amount must be positive."}, status=400)
        except (TypeError, ValueError):
            return Response({"detail": "Invalid amount."}, status=400)

        wallet, _ = Wallet.objects.get_or_create(user=request.user)
        wallet.balance += amount
        wallet.save()

        TransactionHistory.objects.create(
            user=request.user, sender=request.user, receiver=request.user,
            amount=amount, transaction_type="top_up", status="completed",
            description="Wallet top-up"
        )

        return Response({"detail": "Top-up successful."}, status=200)


class WalletWithdrawView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        amount = request.data.get("amount")
        try:
            amount = float(amount)
            if amount <= 0:
                return Response({"detail": "Amount must be positive."}, status=400)
        except (TypeError, ValueError):
            return Response({"detail": "Invalid amount."}, status=400)

        try:
            with transaction.atomic():
                wallet = Wallet.objects.select_for_update().get(user=request.user)

                if not wallet.can_withdraw(amount):
                    return Response({"detail": "Insufficient funds or wallet is frozen."}, status=400)

                wallet.balance -= amount
                wallet.save()

                TransactionHistory.objects.create(
                    user=request.user, sender=request.user, receiver=request.user,
                    amount=amount, transaction_type="withdraw", status="completed",
                    description="Wallet withdrawal"
                )
        except Wallet.DoesNotExist:
            return Response({"detail": "Wallet not found."}, status=404)
        except Exception as e:
            return Response({"detail": f"Internal error: {str(e)}"}, status=500)

        return Response({"detail": "Withdrawal successful."}, status=200)


class TransactionHistoryListView(generics.ListAPIView):
    serializer_class = TransactionHistorySerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        qs = TransactionHistory.objects.filter(user=user).order_by('-timestamp')

        params = self.request.query_params
        if tx_type := params.get("type"):
            qs = qs.filter(transaction_type=tx_type)
        if min_amt := params.get("min_amount"):
            try:
                qs = qs.filter(amount__gte=float(min_amt))
            except ValueError:
                pass
        if max_amt := params.get("max_amount"):
            try:
                qs = qs.filter(amount__lte=float(max_amt))
            except ValueError:
                pass
        if start_date := params.get("start_date"):
            qs = qs.filter(timestamp__date__gte=start_date)
        if end_date := params.get("end_date"):
            qs = qs.filter(timestamp__date__lte=end_date)

        return qs


class TransactionPDFExportView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            month = int(request.query_params.get('month'))
            year = int(request.query_params.get('year'))
        except (TypeError, ValueError):
            return Response({"detail": "Month and year must be integers."}, status=400)

        txs = TransactionHistory.objects.filter(
            user=request.user,
            timestamp__month=month,
            timestamp__year=year
        )

        if not txs.exists():
            return Response({"detail": "No transactions found."}, status=404)

        pdf_buffer = generate_statement_pdf(request.user, txs, month, year)
        filename = f"statement_{request.user.username}_{month}_{year}.pdf"
        return FileResponse(pdf_buffer, as_attachment=True, filename=filename, content_type='application/pdf')
