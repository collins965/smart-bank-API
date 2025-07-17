from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from .models import Loan
from .serializers import LoanSerializer
from .utils import check_loan_eligibility
from accounts.models import Wallet
from decimal import Decimal


class LoanApplicationView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        amount = request.data.get('amount')

        try:
            amount = Decimal(amount)
            if amount <= 0:
                raise ValueError
        except:
            return Response({"detail": "Invalid loan amount"}, status=400)

        score = check_loan_eligibility(user)
        if score < 60:
            return Response({
                "detail": "You are not eligible for a loan",
                "score": score
            }, status=403)

        #  Prevent multiple active loans
        if Loan.objects.filter(user=user, status='approved').exists():
            return Response({"detail": "You already have an active loan"}, status=400)

        loan = Loan.objects.create(
            user=user,
            amount=amount,
            score=score,
            status='approved'
            # interest_rate and total_due auto-calculated in model's save()
        )

        try:
            wallet = Wallet.objects.get(user=user)
            wallet.balance += amount
            wallet.save()
        except Wallet.DoesNotExist:
            return Response({"detail": "Wallet not found"}, status=404)

        return Response(LoanSerializer(loan).data, status=201)


class LoanListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        loans = Loan.objects.filter(user=request.user).order_by('-applied_at')
        return Response(LoanSerializer(loans, many=True).data)


class LoanRepayView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, loan_id):
        user = request.user
        loan = Loan.objects.filter(id=loan_id, user=user).first()

        if not loan:
            return Response({"detail": "Loan not found"}, status=404)

        if loan.status != 'approved':
            return Response({"detail": "Loan already repaid or not eligible for repayment"}, status=400)

        try:
            wallet = Wallet.objects.get(user=user)
        except Wallet.DoesNotExist:
            return Response({"detail": "Wallet not found"}, status=404)

        #  Use total_due for repayment
        if wallet.balance < loan.total_due:
            return Response({"detail": "Insufficient wallet balance"}, status=400)

        wallet.balance -= loan.total_due
        wallet.save()

        loan.status = 'repaid'
        loan.save()

        return Response({"detail": "Loan repaid successfully"}, status=200)
