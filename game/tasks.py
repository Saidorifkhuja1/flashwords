from celery import shared_task
from django.utils import timezone
from datetime import timedelta
from .models import BattleInvitation, UserStatus

@shared_task
def expire_old_invitations():
    """5 daqiqadan eski takliflarni o'chirish"""
    expired_time = timezone.now() - timedelta(minutes=5)
    expired_invitations = BattleInvitation.objects.filter(
        created_at__lt=expired_time,
        status='pending'
    )
    expired_invitations.delete()

@shared_task
def cleanup_offline_users():
    """10 daqiqadan ko'p faol bo'lmagan userlarni offline qilish"""
    inactive_time = timezone.now() - timedelta(minutes=10)
    UserStatus.objects.filter(
        last_activity__lt=inactive_time
    ).update(status='offline')


