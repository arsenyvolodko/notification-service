import asyncio
from datetime import timedelta, datetime

import pytz
from celery import shared_task
import logging
from django.shortcuts import get_object_or_404

from mailing.models import Mailing, Client, Message, MessageStatus
import aiohttp
import os
import dotenv

logger = logging.getLogger(__name__)

dotenv.load_dotenv()


@shared_task
def send_mail_task(message_id: int):
    try:
        message = get_object_or_404(Message, pk=message_id)
        mailing_id = message.mailing.id
        client_id = message.client.id
        mailing = get_object_or_404(Mailing, pk=mailing_id)
        client = get_object_or_404(Client, pk=client_id)
    except Exception:
        return
    if message.status == MessageStatus.SENT:
        return  # happens if mailing start time has been changed to the past and message was already sent
    now = datetime.now().astimezone(pytz.timezone(client.timezone))
    if now > mailing.end_time:  # ran out of time to send
        message.status = MessageStatus.FAILED
        message.save()
        return
    if now < mailing.start_time:
        return  # message will be sent later, it is already in the queue, happens if mailing start time has been changed to the future
    if not check_filters(mailing, client):
        return
    try:
        send_message(message_id, mailing.text, client.phone_number)
    except Exception:
        return  # mailing or client has been deleted during the process, so don't need to send


def check_filters(mailing: Mailing, client: Client):
    if mailing.codes_filter:
        if client.operator_code not in mailing.codes_filter:
            return False
    if mailing.tags_filter:
        if client.tag not in mailing.tags_filter:
            return False
    return True


def send_message(message_id: int, text: str, phone_number: int):
    # url = os.environ['BASE_URL'].format(message_id)
    url = f"https://probe.fbrq.cloud/v1/send/{message_id}"
    headers = {
        'accept': 'application/json',
        'Content-Type': 'application/json',
        'Authorization': os.environ['AUTHORIZATION']
    }
    data = {
        "id": message_id,
        "phone": phone_number,
        "text": text
    }
    sent = asyncio.run(send_msg_to_client(url=url, headers=headers, data=data))
    message = get_object_or_404(Message, pk=message_id)
    if sent:
        message.status = MessageStatus.SENT
        message.sent_time = datetime.now()
        message.save()
        return

    new_time = datetime.now() + timedelta(minutes=5)
    message.status = MessageStatus.FAILED_WAITING
    message.save()
    send_mail_task.apply_async(args=[message.id], eta=new_time)


async def send_msg_to_client(url, headers, data):
    async with aiohttp.ClientSession() as session:
        async with session.post(url=url, headers=headers, json=data) as response:
            return response.status == 200
