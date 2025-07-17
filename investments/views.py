from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from django.shortcuts import get_object_or_404
from .models import Investment
from .serializers import InvestmentSerializer
from .utils import fetch_current_price


class InvestmentListCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """List all investments for the logged-in user"""
        investments = Investment.objects.filter(user=request.user).order_by('-last_updated')
        serializer = InvestmentSerializer(investments, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        """Create a new investment"""
        data = request.data.copy()
        data['user'] = request.user.id
        serializer = InvestmentSerializer(data=data)

        if serializer.is_valid():
            investment = serializer.save()

            # Get and update current price
            try:
                current_price = fetch_current_price(investment.asset_type, investment.symbol)
                investment.update_value(current_price)
            except Exception as e:
                return Response(
                    {"detail": f"Investment saved but price fetch failed: {str(e)}"},
                    status=status.HTTP_207_MULTI_STATUS
                )

            return Response(InvestmentSerializer(investment).data, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UpdateInvestmentValueView(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request, investment_id):
        """Update current price and value of a specific investment"""
        investment = get_object_or_404(Investment, id=investment_id, user=request.user)
        try:
            price = fetch_current_price(investment.asset_type, investment.symbol)
            investment.update_value(price)
            return Response({
                "detail": "Investment value updated",
                "current_price": price,
                "total_value": investment.total_value
            }, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"detail": f"Failed to fetch price: {str(e)}"}, status=400)
