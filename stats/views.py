from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from mailing.models import Mailing, Message, MessageStatus


def get_messages_num(**kwargs):
    return Message.objects.filter(**kwargs).count()


def get_messages_stats(**kwargs):
    return {
        'sent_messages': get_messages_num(status=MessageStatus.SENT, **kwargs),
        'failed_messages': get_messages_num(status=MessageStatus.FAILED, **kwargs),
        'waiting_messages': get_messages_num(status=MessageStatus.WAITING, **kwargs),
        'failed_waiting_messages': get_messages_num(status=MessageStatus.FAILED_WAITING, **kwargs),
    }


def get_common_stats_util():
    mailing_num = Mailing.objects.all().count()
    data = {'mailing_num': mailing_num}
    data.update(get_messages_stats())
    return data


@api_view(['GET'])
def get_common_stats_api(request):
    data = get_common_stats_util()
    return Response(data, status=status.HTTP_200_OK)


def get_spec_stats_util(mailing_id: int):
    get_object_or_404(Mailing, pk=mailing_id)
    data = {'mailing_id': mailing_id}
    data.update(get_messages_stats(mailing=mailing_id))
    return data


@api_view(['GET'])
def get_spec_stats_api(request, mailing_id: int):
    data = get_spec_stats_util(mailing_id)
    return Response(data, status=status.HTTP_200_OK)
