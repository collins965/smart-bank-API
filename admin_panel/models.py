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
        User,
        on_delete=models.CASCADE,
        related_name='admin_actions',
        help_text='The admin who performed the action'
    )
    action = models.CharField(
        max_length=50,
        choices=ACTION_CHOICES,
        help_text='The type of admin action performed'
    )
    target_user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='affected_users',
        null=True,
        blank=True,
        help_text='The user affected by the admin action (if applicable)'
    )
    loan = models.ForeignKey(
        Loan,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        help_text='The loan affected by the admin action (if applicable)'
    )
    transaction = models.ForeignKey(
        MpesaTransaction,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        help_text='The transaction affected by the admin action (if applicable)'
    )
    timestamp = models.DateTimeField(
        auto_now_add=True,
        help_text='Timestamp when the action was performed'
    )
    notes = models.TextField(
        blank=True,
        help_text='Additional notes or context about the action'
    )

    class Meta:
        ordering = ['-timestamp']
        verbose_name = 'Admin Action Log'
        verbose_name_plural = 'Admin Action Logs'

    def __str__(self):
        return f"{self.admin_user.username} performed {self.get_action_display()} on {self.timestamp.strftime('%Y-%m-%d %H:%M:%S')}"
