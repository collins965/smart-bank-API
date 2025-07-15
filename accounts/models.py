from django.db import models
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password, check_password
import uuid


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    id_number = models.CharField(max_length=20, blank=True, null=True, unique=True)
    phone = models.CharField(max_length=15, blank=True, null=True)
    date_of_birth = models.DateField(blank=True, null=True)
    address = models.CharField(max_length=255, blank=True, null=True)
    bio = models.TextField(blank=True, null=True)
    profile_image = models.ImageField(upload_to='profiles/', default='profiles/default.png')
    transfer_pin = models.CharField(max_length=128, blank=True, null=True)  # Hashed PIN

    def __str__(self):
        return self.user.username

    def set_transfer_pin(self, raw_pin):
        self.transfer_pin = make_password(raw_pin)
        self.save()

    def check_transfer_pin(self, raw_pin):
        return check_password(raw_pin, self.transfer_pin)


class Wallet(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='wallet')
    account_number = models.CharField(max_length=12, unique=True, editable=False)
    balance = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.account_number:
            self.account_number = str(uuid.uuid4().int)[:12]
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.user.username} - {self.account_number}"


class Transaction(models.Model):
    TRANSACTION_TYPES = (
        ('top_up', 'Top-Up'),
        ('withdraw', 'Withdraw'),
        ('transfer', 'Transfer'),
    )

    sender_wallet = models.ForeignKey(
        Wallet, on_delete=models.SET_NULL,
        related_name='sent_transactions',
        null=True, blank=True
    )
    recipient_wallet = models.ForeignKey(
        Wallet, on_delete=models.SET_NULL,
        related_name='received_transactions',
        null=True, blank=True
    )
    transaction_type = models.CharField(max_length=10, choices=TRANSACTION_TYPES)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    timestamp = models.DateTimeField(auto_now_add=True)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.transaction_type.upper()} - KSh {self.amount}"
