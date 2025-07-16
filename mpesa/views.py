# mpesa/views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.conf import settings
from .daraja import initiate_stk_push
from .models import MpesaTransaction
from accounts.models import Wallet
import logging

logger = logging.getLogger(__name__)


class STKPushView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        phone = request.data.get("phone")
        amount = request.data.get("amount")
        reference = request.data.get("reference", "SmartBank360")
        description = request.data.get("description", "Deposit to wallet")

        if not phone or not amount:
            return Response({"detail": "Phone and amount are required."}, status=400)

        try:
            amount = int(amount)
            if amount <= 0:
                return Response({"detail": "Amount must be greater than zero."}, status=400)
        except (ValueError, TypeError):
            return Response({"detail": "Invalid amount."}, status=400)

        try:
            response = initiate_stk_push(phone, amount, reference, description)

            if "errorCode" in response or "errorMessage" in response:
                logger.error("STK Push Error: %s", response)
                return Response(response, status=500)

            MpesaTransaction.objects.create(
                user=user,
                phone_number=phone,
                amount=amount,
                account_reference=reference,
                description=description,
                checkout_request_id=response.get("CheckoutRequestID", ""),
                merchant_request_id=response.get("MerchantRequestID", ""),
                status='pending',
            )

            return Response({
                "detail": "STK Push request sent successfully.",
                "response": response
            }, status=200)

        except Exception as e:
            logger.exception("Unhandled STK Push error")
            return Response({"detail": "STK Push failed", "error": str(e)}, status=500)


@method_decorator(csrf_exempt, name='dispatch')
class STKCallbackView(APIView):
    permission_classes = [AllowAny]  # Safaricom won’t send token

    def post(self, request):
        logger.info("Received M-Pesa callback: %s", request.data)

        callback = request.data.get("Body", {}).get("stkCallback", {})
        checkout_id = callback.get("CheckoutRequestID")
        result_code = callback.get("ResultCode")
        result_desc = callback.get("ResultDesc")

        try:
            transaction = MpesaTransaction.objects.get(checkout_request_id=checkout_id)
        except MpesaTransaction.DoesNotExist:
            logger.warning("Transaction not found for callback: %s", checkout_id)
            return Response({"detail": "Transaction not found"}, status=404)

        transaction.result_code = result_code
        transaction.result_desc = result_desc

        if result_code == 0:
            # Extract metadata
            metadata = callback.get("CallbackMetadata", {}).get("Item", [])
            receipt = next((item["Value"] for item in metadata if item["Name"] == "MpesaReceiptNumber"), None)

            transaction.mpesa_receipt_number = receipt
            transaction.status = 'completed'

            # Update wallet balance
            wallet = Wallet.objects.get(user=transaction.user)
            wallet.balance += transaction.amount
            wallet.save()
            logger.info("Wallet updated for user %s with KSh %.2f", transaction.user.username, transaction.amount)
        else:
            transaction.status = 'failed'

        transaction.save()
        return Response({"detail": "Callback processed"}, status=200)
