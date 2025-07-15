# mpesa/views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.conf import settings
from .daraja import initiate_stk_push
from .models import MpesaTransaction
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

            # Check for Daraja error
            if "errorCode" in response or "errorMessage" in response:
                logger.error("STK Push Error: %s", response)
                return Response(response, status=500)

            # Log transaction in database
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
