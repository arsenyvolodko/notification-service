from datetime import datetime

from django.core.handlers.wsgi import WSGIRequest
from django.shortcuts import render, redirect, get_object_or_404
import pytz
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

import notification_service.settings
import stats.views
from clients.models import Client
from notification_service.views import login_required
from .forms import MailingForm
from .models import Mailing, Message, MessageStatus
from .serializers import MailingSerializer
from .tasks import send_mail_task


def get_mailings_and_stats():
    previous_mailings = Mailing.get_previous_mailings().order_by('id')
    current_mailings = Mailing.get_current_mailings().order_by('id')
    future_mailings = Mailing.get_future_mailings().order_by('id')

    previous_messages = {mailing.id: stats.views.get_messages_stats(mailing=mailing.id) for mailing in
                         previous_mailings}
    current_messages = {mailing.id: stats.views.get_messages_stats(mailing=mailing.id) for mailing in
                        current_mailings}
    future_messages = {mailing.id: stats.views.get_messages_stats(mailing=mailing.id) for mailing in future_mailings}

    return {
        'previous_mailings': Mailing.get_previous_mailings(),
        'current_mailings': Mailing.get_current_mailings(),
        'future_mailings': Mailing.get_future_mailings(),

        'previous_messages': previous_messages,
        'current_messages': current_messages,
        'future_messages': future_messages
    }


@login_required
def mailing(request: WSGIRequest):
    # generate()
    return render(request, "mailing/mailing.html", context=get_mailings_and_stats())


# add mailing

def create_mailing_util(data):
    form = MailingForm(data)
    validate_form(form)
    new_mailing = form.save()
    create_messages(new_mailing)
    return new_mailing


@login_required
def create_mailing(request: WSGIRequest):
    if request.method == 'GET':
        return render(request, "mailing/add_mailing.html", {'form': MailingForm})
    elif request.method == 'POST':
        try:
            create_mailing_util(request.POST)
            return redirect('mailing:mailing')
        except ValueError as e:
            return render(request, 'mailing/add_mailing.html',
                          {'form': MailingForm(request.POST), 'error': e})


@api_view(['POST'])
def create_mailing_api(request):
    try:
        new_mailing = create_mailing_util(request.data)
        serializer = MailingSerializer(new_mailing)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    except ValueError as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


# update mailing


def update_mailing_util(form: MailingForm, mailing_id: int):
    old_mailing = get_object_or_404(Mailing, pk=mailing_id)
    new_mailing = validate_form(form)
    form.save(commit=False)
    time_changed = old_mailing.end_time != new_mailing.end_time or old_mailing.start_time != new_mailing.start_time
    filters_changed = old_mailing.tags_filter != new_mailing.tags_filter or old_mailing.codes_filter != new_mailing.codes_filter
    form.save()
    if time_changed or filters_changed:
        update_messages(new_mailing, time_changed=time_changed, filters_changed=filters_changed)


@login_required
def update_mailing(request: WSGIRequest, mailing_id: int):
    mailing_to_edit = get_object_or_404(Mailing, pk=mailing_id)
    if request.method == 'POST':
        try:
            update_mailing_util(MailingForm(request.POST, instance=mailing_to_edit), mailing_id)
            return redirect('mailing:mailing')
        except ValueError as e:
            return render(request, 'mailing/add_mailing.html',
                          {'form': MailingForm(request.POST), 'error': e})
    else:
        form = MailingForm(instance=mailing_to_edit)
    return render(request, 'mailing/add_mailing.html', {'form': form, 'mailing': mailing_to_edit})


@api_view(['PATCH'])
def update_mailing_api(request, mailing_id: int):
    mailing_to_update = get_object_or_404(Mailing, pk=mailing_id)
    try:
        old_data = MailingSerializer(mailing_to_update).data
        new_data = {**old_data, **request.data}
        update_mailing_util(MailingForm(new_data, instance=mailing_to_update), mailing_id)
    except ValueError as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    return Response(status=status.HTTP_200_OK)


# delete mailing

def delete_mailing_util(mailing: Mailing):
    mailing.delete()


@login_required
def delete_mailing(request: WSGIRequest, mailing_id: int):
    mailing_to_delete = get_object_or_404(Mailing, pk=mailing_id)
    try:
        if request.method == 'POST':
            delete_mailing_util(mailing_to_delete)
    except Exception as e:
        return render(request, 'mailing/mailing.html', {'error': 'Cannot delete mailing: ' + str(e)})
    return redirect('mailing:mailing')


@api_view(['DELETE'])
def delete_mailing_api(request, mailing_id: int):
    mailing_to_delete = get_object_or_404(Mailing, pk=mailing_id)
    try:
        delete_mailing_util(mailing_to_delete)
    except Exception as e:
        return Response({'error': 'Cannot delete mailing: ' + str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    return Response(status=status.HTTP_200_OK)


# utils

def eval_time(start_time, timezone):
    return start_time.astimezone(pytz.timezone(timezone))


def create_messages(mailing: Mailing):
    clients = Client.get_clients_by_tags_and_codes(tags=mailing.tags_filter, codes=mailing.codes_filter)
    for client in clients:
        message = Message.objects.create(mailing=mailing, client=client)
        send_time = eval_time(mailing.start_time, client.timezone)
        add_to_queue(message.id, send_time)


def add_to_queue(message_id: int, send_time) -> None:
    now = datetime.now(pytz.timezone(notification_service.settings.TIME_ZONE))
    if send_time < now:
        send_mail_task.apply_async(args=[message_id])
    else:
        send_mail_task.apply_async(args=[message_id], eta=send_time)


def validate_form(form: MailingForm):
    if not form.is_valid():
        raise ValueError(form.errors)
    new_mailing = form.save(commit=False)
    if new_mailing.end_time < datetime.now(pytz.timezone(notification_service.settings.TIME_ZONE)):
        raise ValueError("End time is in the past")
    if new_mailing.end_time < new_mailing.start_time:
        raise ValueError("End time is before start time")
    return new_mailing


def update_messages(mailing: Mailing, time_changed: bool, filters_changed: bool):
    messages = list(Message.objects.filter(mailing=mailing.id,
                                           status__in=[MessageStatus.WAITING, MessageStatus.FAILED_WAITING,
                                                       MessageStatus.FAILED]).all())
    clients = {message.client for message in messages}
    if filters_changed:
        additional_clients = [i for i in
                              Client.get_clients_by_tags_and_codes(tags=mailing.tags_filter, codes=mailing.codes_filter)
                              if i not in clients]
        for client in additional_clients:
            message = Message.objects.create(mailing=mailing, client=client)
            messages.append(message)

    if time_changed:
        for message in messages:
            send_time = eval_time(mailing.start_time, message.client.timezone)
            add_to_queue(message.id, send_time)
