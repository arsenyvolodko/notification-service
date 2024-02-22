from django.forms import ModelForm, Select

from . import models
from .models import Client


class ClientForm(ModelForm):
    class Meta:
        model = Client
        fields = [
            'phone_number',
            'tag',
            'timezone'
        ]
        widgets = {
            'timezone': Select(choices=models.TIMEZONE_CHOICES)
        }
