from django.forms import ModelForm

from .models import Mailing


class MailingForm(ModelForm):
    class Meta:
        model = Mailing
        fields = [
            'start_time',
            'text',
            'codes_filter',
            'tags_filter',
            'end_time',
        ]
