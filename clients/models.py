from django.db import models
import pytz

TIMEZONE_CHOICES = [(tz, tz) for tz in pytz.all_timezones]


class Client(models.Model):
    phone_number = models.PositiveBigIntegerField(blank=False, null=False)
    operator_code = models.IntegerField(blank=False, null=False)
    tag = models.CharField(blank=True, null=True, max_length=150)
    timezone = models.CharField(blank=False, null=False, max_length=100, choices=TIMEZONE_CHOICES,
                                default='UTC')

    @classmethod
    def get_clients_by_tags_and_codes(cls, tags: list[str], codes: list[int]):
        if not tags and not codes:
            return cls.objects.all()
        if not tags:
            return cls.objects.filter(operator_code__in=codes)
        if not codes:
            return cls.objects.filter(tag__in=tags)
        return cls.objects.filter(tag__in=tags, operator_code__in=codes)
