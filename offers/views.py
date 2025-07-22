from rest_framework import generics, permissions
from offers.models import ExclusiveOffer
from .serializers import ExclusiveOfferSerializer


class ExclusiveOfferListCreateView(generics.ListCreateAPIView):
    """
    GET: Anyone can view the list of exclusive offers.
    POST: Only admins can create a new offer.
    """
    queryset = ExclusiveOffer.objects.all().order_by('-created_at')
    serializer_class = ExclusiveOfferSerializer

    def get_permissions(self):
        if self.request.method == 'POST':
            return [permissions.IsAdminUser()]
        return [permissions.AllowAny()]


class ExclusiveOfferDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    GET: Anyone can view a single offer.
    PUT/PATCH/DELETE: Only admins can update or delete an offer.
    """
    queryset = ExclusiveOffer.objects.all()
    serializer_class = ExclusiveOfferSerializer

    def get_permissions(self):
        if self.request.method in ['PUT', 'PATCH', 'DELETE']:
            return [permissions.IsAdminUser()]
        return [permissions.AllowAny()]
# offers/views.py

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAdminUser
from .models import ExclusiveOffer
from .serializers import ExclusiveOfferSerializer

class AdminExclusiveOfferList(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        offers = ExclusiveOffer.objects.all()
        serializer = ExclusiveOfferSerializer(offers, many=True)
        return Response(serializer.data)
