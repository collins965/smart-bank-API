from django.db import models
from django.contrib.auth.models import User

class Investment(models.Model):
    ASSET_CHOICES = [
        ('stock', 'Stock'),
        ('crypto', 'Crypto'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='investments')
    asset_type = models.CharField(max_length=10, choices=ASSET_CHOICES)
    symbol = models.CharField(max_length=10)
    units = models.DecimalField(max_digits=12, decimal_places=6)
    buy_price = models.DecimalField(max_digits=12, decimal_places=4, default=0.0)  # ✅ new field
    current_price = models.DecimalField(max_digits=12, decimal_places=4, default=0.0)
    total_value = models.DecimalField(max_digits=15, decimal_places=4, default=0.0)
    last_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.symbol} - {self.units} units"

    def update_value(self, price):
        self.current_price = price
        self.total_value = price * self.units
        self.save()

    @property
    def initial_value(self):
        return self.units * self.buy_price
