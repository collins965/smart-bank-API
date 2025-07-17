from django.db import models
from accounts.models import User
from loans.models import Loan
from mpesa.models import MpesaTransaction


class AdminActionLog(models.Model):
    ACTION_CHOICES = [
        ('activate_user', 'Activate User'),
        ('deactivate_user', 'Deactivate User'),
        ('approve_loan', 'Approve Loan'),
        ('reject_loan', 'Reject Loan'),
        ('freeze_wallet', 'Freeze Wallet'),
        ('unfreeze_wallet', 'Unfreeze Wallet'),
    ]

    admin_user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='admin_actions'
    )
    action = models.CharField(
        max_length=50, choices=ACTION_CHOICES
    )
    target_user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='affected_users',
        null=True, blank=True
    )
    loan = models.ForeignKey(
        Loan, on_delete=models.SET_NULL,
        null=True, blank=True
    )
    transaction = models.ForeignKey(
        MpesaTransaction, on_delete=models.SET_NULL,
        null=True, blank=True
    )
    timestamp = models.DateTimeField(auto_now_add=True)
    notes = models.TextField(blank=True)

    def __str__(self):
        return f"{self.admin_user.username} performed {self.get_action_display()} on {self.timestamp.strftime('%Y-%m-%d %H:%M:%S')}"
