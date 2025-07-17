from django.urls import path
from .views import AdminUserList, AdminLoanList, AdminTransactionList

urlpatterns = [
    path('admin/users/', AdminUserList.as_view(), name='admin-users'),
    path('admin/loans/', AdminLoanList.as_view(), name='admin-loans'),
    path('admin/transactions/', AdminTransactionList.as_view(), name='admin-transactions'),
]
