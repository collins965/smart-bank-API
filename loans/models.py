from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta

class Loan(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('repaid', 'Repaid'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='loans')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    applied_at = models.DateTimeField(auto_now_add=True)
    repayment_date = models.DateField(default=timezone.now() + timedelta(days=30))
    score = models.IntegerField(default=0)  # Eligibility score (0–100)

    def __str__(self):
        return f"Loan {self.id} | {self.user.username} | {self.status}"
