from django.urls import path
from .views import (
    UserRegistrationView,
    WalletDetailView,
    SetTransferPinView,
    MakeTransferView,
    TransactionHistoryListView,
    TransactionPDFExportView,
    WalletTopUpView,
    WalletWithdrawView,
)
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

urlpatterns = [
    path('register/', UserRegistrationView.as_view(), name='register'),
    path('login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    path('wallet/', WalletDetailView.as_view(), name='wallet-detail'),

    path('wallet/top-up/', WalletTopUpView.as_view(), name='wallet-top-up'),
    path('wallet/withdraw/', WalletWithdrawView.as_view(), name='wallet-withdraw'),

    path('wallet/set-pin/', SetTransferPinView.as_view(), name='wallet-set-pin'),
    path('wallet/transfer/', MakeTransferView.as_view(), name='wallet-transfer'),

    path('wallet/history/', TransactionHistoryListView.as_view(), name='wallet-transaction-history'),

    path('wallet/statements/pdf/', TransactionPDFExportView.as_view(), name='wallet-statement-pdf'),
]