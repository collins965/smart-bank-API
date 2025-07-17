from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta
from decimal import Decimal

def default_repayment_date():
    return timezone.now().date() + timedelta(days=30)

class Loan(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('repaid', 'Repaid'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='loans')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    interest_rate = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal('10.00'))  # 10% default
    total_due = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    applied_at = models.DateTimeField(auto_now_add=True)
    repayment_date = models.DateField(default=default_repayment_date)
    score = models.IntegerField(default=0)  # Eligibility score (0–100)

    def calculate_total_due(self):
        interest = self.amount * (self.interest_rate / Decimal('100'))
        return self.amount + interest

    def save(self, *args, **kwargs):
        if self.total_due is None:
            self.total_due = self.calculate_total_due()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Loan {self.id} | {self.user.username} | {self.status}"
