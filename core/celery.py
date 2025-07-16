from __future__ import absolute_import, unicode_literals
import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')

app = Celery('flashwords')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()

# Periodic tasks
from celery.schedules import crontab

app.conf.beat_schedule = {
    'expire-invitations': {
        'task': 'game.tasks.expire_old_invitations',
        'schedule': crontab(minute='*/5'),  # Har 5 daqiqada
    },
    'cleanup-offline-users': {
        'task': 'game.tasks.cleanup_offline_users',
        'schedule': crontab(minute='*/10'),  # Har 10 daqiqada
    },
}

app.conf.timezone = 'UTC'


