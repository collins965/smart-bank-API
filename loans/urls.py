from django.urls import path
from .views import LoanApplicationView, LoanListView, LoanRepayView

urlpatterns = [
    path("apply/", LoanApplicationView.as_view(), name="apply-loan"),
    path("", LoanListView.as_view(), name="list-loans"),
    path("repay/<int:loan_id>/", LoanRepayView.as_view(), name="repay-loan"),
]
