from django.urls import path
from .views import InvestmentListCreateView, UpdateInvestmentValueView

urlpatterns = [
    path('', InvestmentListCreateView.as_view(), name='investment-list-create'),
    path('<int:investment_id>/update/', UpdateInvestmentValueView.as_view(), name='investment-update-value'),
]
