from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Notification
from loans.models import Loan
from mpesa.models import Transaction

@receiver(post_save, sender=Transaction)
def notify_on_deposit(sender, instance, **kwargs):
    if instance.status == 'success':
        Notification.objects.create(
            user=instance.user,
            notif_type='deposit_success',
            message=f"Your deposit of {instance.amount} was successful."
        )

@receiver(post_save, sender=Loan)
def notify_loan_due(sender, instance, **kwargs):
    if instance.status == 'due':
        Notification.objects.create(
            user=instance.user,
            notif_type='loan_due',
            message=f"Your loan of {instance.amount} is now due."
        )
