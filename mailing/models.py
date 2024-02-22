import enum
from django.utils import timezone

from django.contrib.postgres.fields import ArrayField
from django.db import models
from django.db.models import CASCADE

from clients.models import Client


class Mailing(models.Model):
    start_time = models.DateTimeField(blank=False, null=False)
    text = models.TextField(blank=False, null=False)
    tags_filter = ArrayField(models.CharField(max_length=50), blank=True, null=True)
    codes_filter = ArrayField(models.IntegerField(), blank=True, null=True)
    end_time = models.DateTimeField(blank=False, null=False)

    @classmethod
    def get_previous_mailings(cls):
        return cls.objects.filter(end_time__lt=timezone.now()).all()

    @classmethod
    def get_current_mailings(cls):
        return cls.objects.filter(start_time__lte=timezone.now(), end_time__gte=timezone.now()).all()

    @classmethod
    def get_future_mailings(cls):
        return cls.objects.filter(start_time__gt=timezone.now()).all()


class MessageStatus(enum.Enum):
    WAITING = enum.auto()  # waiting to be sent for the first time
    SENT = enum.auto()  # successfully sent
    FAILED_WAITING = enum.auto()  # didn't send, but will be sent again
    FAILED = enum.auto()  # didn't send and won't be sent again


class Message(models.Model):
    sent_time = models.DateTimeField(blank=True, null=True)
    status = models.CharField(blank=False, null=False, default=MessageStatus.WAITING, max_length=50)
    mailing = models.ForeignKey(Mailing, on_delete=CASCADE, related_name='messages')
    client = models.ForeignKey(Client, on_delete=CASCADE, related_name='received_messages')

    async def update_status(self, new_status: MessageStatus):
        self.status = new_status
        await self.save()
