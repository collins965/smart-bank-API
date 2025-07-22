# accounts/signals.py

from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from .models import Profile, Wallet
import logging

logger = logging.getLogger(__name__)

@receiver(post_save, sender=User)
def create_profile_and_wallet(sender, instance, created, **kwargs):
    """
    Automatically create Profile and Wallet when a new User is created.
    """
    if created:
        try:
            profile, created_profile = Profile.objects.get_or_create(user=instance)
            wallet, created_wallet = Wallet.objects.get_or_create(user=instance)

            if created_profile:
                logger.info(f"Profile created for user {instance.username}.")
            if created_wallet:
                logger.info(f"Wallet created for user {instance.username}.")
        except Exception as e:
            logger.error(f"Error creating profile or wallet for user {instance.username}: {e}")

@receiver(post_save, sender=User)
def save_profile_and_wallet(sender, instance, **kwargs):
    """
    Save associated Profile and Wallet whenever the User instance is updated.
    """
    try:
        if hasattr(instance, 'profile') and instance.profile:
            instance.profile.save()
            logger.info(f"Profile saved for user {instance.username}.")
    except ObjectDoesNotExist:
        logger.warning(f"Profile does not exist for user {instance.username}.")
    except Exception as e:
        logger.error(f"Error saving profile for user {instance.username}: {e}")

    try:
        if hasattr(instance, 'wallet') and instance.wallet:
            instance.wallet.save()
            logger.info(f"Wallet saved for user {instance.username}.")
    except ObjectDoesNotExist:
        logger.warning(f"Wallet does not exist for user {instance.username}.")
    except Exception as e:
        logger.error(f"Error saving wallet for user {instance.username}: {e}")
