from django.contrib import admin
from .models import TransactionHistory

@admin.register(TransactionHistory)
class TransactionHistoryAdmin(admin.ModelAdmin):
    list_display = ('user', 'type', 'amount', 'status', 'timestamp')
    list_filter = ('type', 'status', 'timestamp')
    search_fields = ('user__username', 'sender', 'receiver')
