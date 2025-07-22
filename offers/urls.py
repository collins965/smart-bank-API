from django.urls import path
from .views import ExclusiveOfferListCreateView, ExclusiveOfferDetailView

urlpatterns = [
    path('exclusive-offers/', ExclusiveOfferListCreateView.as_view(), name='exclusive-offer-list'),
    path('exclusive-offers/<int:pk>/', ExclusiveOfferDetailView.as_view(), name='exclusive-offer-detail'),
]
