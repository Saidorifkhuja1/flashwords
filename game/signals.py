from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import UserStatus

@receiver(post_save, sender=User)
def create_user_status(sender, instance, created, **kwargs):
    if created:
        UserStatus.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_status(sender, instance, **kwargs):
    UserStatus.objects.get_or_create(user=instance)


