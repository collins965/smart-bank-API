from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import Loan
from .serializers import LoanSerializer
from .utils import check_loan_eligibility
from accounts.models import Wallet
from datetime import date
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
            return Response({"detail": "Invalid amount"}, status=400)

        score = check_loan_eligibility(user)

        if score < 60:
            return Response({"detail": "You are not eligible for a loan", "score": score}, status=403)

        loan = Loan.objects.create(
            user=user,
            amount=amount,
            score=score,
            status='approved',
        )

        # Credit loan to wallet
        wallet = Wallet.objects.get(user=user)
        wallet.balance += amount
        wallet.save()

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
            return Response({"detail": "Loan already repaid or invalid"}, status=400)

        wallet = user.wallet
        if wallet.balance < loan.amount:
            return Response({"detail": "Insufficient wallet balance"}, status=400)

        wallet.balance -= loan.amount
        wallet.save()

        loan.status = 'repaid'
        loan.save()

        return Response({"detail": "Loan repaid successfully"}, status=200)
