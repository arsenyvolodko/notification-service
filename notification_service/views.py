import json
from authlib.integrations.django_client import OAuth
from django.conf import settings
from django.shortcuts import redirect, render, redirect
from urllib.parse import quote_plus, urlencode
from functools import wraps
from django.http import HttpResponseRedirect
from django.urls import reverse

from clients.models import Client
from mailing.models import Mailing
from stats.views import get_messages_stats

oauth = OAuth()

oauth.register(
    "auth0",
    client_id=settings.AUTH0_CLIENT_ID,
    client_secret=settings.AUTH0_CLIENT_SECRET,
    client_kwargs={
        "scope": "openid profile email",
    },
    server_metadata_url=f"https://{settings.AUTH0_DOMAIN}/.well-known/openid-configuration",
)


def login_required(f):
    @wraps(f)
    def wrap(request, *args, **kwargs):
        if "user" not in request.session:
            return HttpResponseRedirect(reverse('login'))
        return f(request, *args, **kwargs)

    return wrap


def home(request):
    return render(
        request,
        "notification_service/home.html",
        context={
            "session": request.session.get("user"),
            "pretty": json.dumps(request.session.get("user"), indent=4),
            "messages": get_messages_stats(),
            "clients_num": len(Client.objects.all()),
            "mailing_num": len(Mailing.objects.all())
        },
    )


def callback(request):
    token = oauth.auth0.authorize_access_token(request)
    request.session["user"] = token
    return redirect(request.build_absolute_uri(reverse("home")))


def login(request):
    return oauth.auth0.authorize_redirect(
        request, request.build_absolute_uri(reverse("callback"))
    )


def logout(request):
    request.session.clear()

    return redirect(
        f"https://{settings.AUTH0_DOMAIN}/v2/logout?"
        + urlencode(
            {
                "returnTo": request.build_absolute_uri(reverse("home")),
                "client_id": settings.AUTH0_CLIENT_ID,
            },
            quote_via=quote_plus,
        ),
    )
