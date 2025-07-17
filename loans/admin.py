from django.contrib import admin
from .models import Loan

@admin.register(Loan)
class LoanAdmin(admin.ModelAdmin):
    list_display = ('user', 'amount', 'status', 'score', 'applied_at', 'repayment_date')
    list_filter = ('status', 'repayment_date')
    search_fields = ('user__username', 'user__email')
    ordering = ('-applied_at',)
