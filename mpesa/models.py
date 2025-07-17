from django.db import models
from django.conf import settings


class MpesaTransaction(models.Model):
    """
    Logs M-Pesa STK Push transactions initiated by users.
    """

    # Status choices
    TRANSACTION_STATUS = (
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('cancelled', 'Cancelled'),
    )

    # User and basic transaction data
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='mpesa_transactions',
        help_text="The user who initiated the transaction"
    )

    phone_number = models.CharField(
        max_length=13,
        help_text="Phone number in format 2547XXXXXXXX"
    )

    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text="Amount transacted via M-Pesa"
    )

    account_reference = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        help_text="Account reference used during STK Push"
    )

    description = models.TextField(
        blank=True,
        null=True,
        help_text="Optional description or transaction note"
    )

    # Safaricom API identifiers and response fields
    checkout_request_id = models.CharField(
        max_length=100,
        unique=True,
        help_text="Unique CheckoutRequestID from Safaricom"
    )

    merchant_request_id = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        help_text="MerchantRequestID from Safaricom"
    )

    mpesa_receipt_number = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        help_text="Receipt number from successful M-Pesa transaction"
    )

    result_code = models.CharField(
        max_length=10,
        blank=True,
        null=True,
        help_text="Safaricom ResultCode (e.g., 0 for success)"
    )

    result_desc = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        help_text="Safaricom ResultDesc (result description)"
    )

    # Transaction status tracking
    status = models.CharField(
        max_length=20,
        choices=TRANSACTION_STATUS,
        default='pending',
        help_text="Current status of the transaction"
    )

    # Timestamps
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="Timestamp when transaction was created"
    )

    updated_at = models.DateTimeField(
        auto_now=True,
        help_text="Timestamp when transaction was last updated"
    )

    def __str__(self):
        return f"{self.user.username} | {self.amount} KES | {self.status}"

    class Meta:
        ordering = ['-created_at']
        verbose_name = "M-Pesa Transaction"
        verbose_name_plural = "M-Pesa Transactions"
