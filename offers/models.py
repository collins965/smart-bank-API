from django.db import models
from django.contrib.auth.models import User

class ExclusiveOffer(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField()
    discount = models.DecimalField(max_digits=5, decimal_places=2)
    valid_until = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.title
