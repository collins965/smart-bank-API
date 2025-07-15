from django.urls import path
from .views import (
    RegisterView,
    ProfileDetailView,
    ProfileUpdateView,
    WalletDetailView,
    TransactionListView,
    TransactionCreateView,
)
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    path('profile/', ProfileDetailView.as_view(), name='profile-detail'),
    path('profile/update/', ProfileUpdateView.as_view(), name='profile-update'),

    # Wallet endpoints
    path('wallet/', WalletDetailView.as_view(), name='wallet-detail'),

    # Transaction endpoints
    path('wallet/transactions/', TransactionListView.as_view(), name='wallet-transactions'),
    path('wallet/transactions/new/', TransactionCreateView.as_view(), name='wallet-transaction-create'),
]
