from django.db import models
from django.contrib.auth.models import User

class Notification(models.Model):
    NOTIF_TYPES = [
        ('low_balance', 'Low Balance'),
        ('loan_due', 'Loan Due'),
        ('deposit_success', 'Deposit Success'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="notifications")
    notif_type = models.CharField(max_length=20, choices=NOTIF_TYPES)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.notif_type}"
