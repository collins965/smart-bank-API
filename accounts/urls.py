from django.urls import path
from .views import (
    RegisterView,
    ProfileDetailView,
    ProfileUpdateView,
    WalletDetailView,
    TransactionListView,
    TransactionCreateView,
    SetTransferPinView,
    TransferView,
    TransactionHistoryListView,
)
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

urlpatterns = [
    # --- Auth ---
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    # --- Profile ---
    path('profile/', ProfileDetailView.as_view(), name='profile-detail'),
    path('profile/update/', ProfileUpdateView.as_view(), name='profile-update'),

    # --- Wallet ---
    path('wallet/', WalletDetailView.as_view(), name='wallet-detail'),

    # --- Transactions ---
    path('wallet/transactions/', TransactionListView.as_view(), name='wallet-transactions'),
    path('wallet/transactions/new/', TransactionCreateView.as_view(), name='wallet-transaction-create'),

    # --- PIN & Transfers ---
    path('wallet/set-pin/', SetTransferPinView.as_view(), name='wallet-set-pin'),
    path('wallet/transfer/', TransferView.as_view(), name='wallet-transfer'),

    # --- Transaction History Logs ---
    path('wallet/history/', TransactionHistoryListView.as_view(), name='wallet-transaction-history'),
]
