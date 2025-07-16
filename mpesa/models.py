# mpesa/models.py
from django.db import models
from django.contrib.auth.models import User

class MpesaTransaction(models.Model):
    """Logs M-Pesa STK Push transactions"""

    TRANSACTION_STATUS = (
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('cancelled', 'Cancelled'),
    )

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='mpesa_transactions'
    )

    phone_number = models.CharField(
        max_length=13,
        help_text="Phone number in format 2547XXXXXXXX"
    )

    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    account_reference = models.CharField(
        max_length=100,
        blank=True,
        null=True
    )

    description = models.TextField(
        blank=True,
        null=True
    )

    # Daraja response data
    checkout_request_id = models.CharField(
        max_length=100,
        unique=True
    )

    merchant_request_id = models.CharField(
        max_length=100,
        blank=True,
        null=True
    )

    mpesa_receipt_number = models.CharField(
        max_length=100,
        blank=True,
        null=True
    )

    result_code = models.CharField(
        max_length=10,
        blank=True,
        null=True
    )

    result_desc = models.CharField(
        max_length=255,
        blank=True,
        null=True
    )

    status = models.CharField(
        max_length=20,
        choices=TRANSACTION_STATUS,
        default='pending'
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    def __str__(self):
        return f"M-Pesa STK Push | {self.user.username} | {self.amount} KES | {self.status}"
