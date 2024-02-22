from __future__ import absolute_import, unicode_literals
import os
from celery import Celery
from django.conf import settings
# from mailing.tasks import send_mail_task
from celery.schedules import crontab

# Set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'notification_service.settings')

app = Celery('notification_service')
app.config_from_object('django.conf:settings', namespace='CELERY')
# app.conf.enable_utc = True
# app.config_from_object(settings, namespace='CELERY')
# app.log.setup_task_loggers(level='INFO')
app.autodiscover_tasks()

