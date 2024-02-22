from django.core.handlers.wsgi import WSGIRequest
from django.shortcuts import render, redirect, get_object_or_404
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from notification_service.views import login_required
from .forms import ClientForm
from .models import Client
from .serializers import ClientSerializer


@login_required
def clients(request):
    return render(request, "clients/clients.html", {
        'clients': Client.objects.all().order_by('id')
    })


# create client

def create_client_util(data):
    form = ClientForm(data)
    new_client = validate_and_save(form)
    return new_client


@login_required
def create_client(request):
    if request.method == 'GET':
        return render(request, "clients/add_client.html", {'form': ClientForm})
    elif request.method == 'POST':
        try:
            create_client_util(request.POST)
            return redirect('clients:clients')
        except ValueError as e:
            return render(request, 'clients/add_client.html',
                          {'form': ClientForm(request.POST), 'error': e})


@api_view(['POST'])
def create_client_api(request):
    try:
        new_client = create_client_util(request.data)
    except ValueError as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
    serializer = ClientSerializer(new_client)
    return Response(serializer.data, status=status.HTTP_201_CREATED)


# update client

def update_client_util(form: ClientForm, client_id: int):
    get_object_or_404(Client, pk=client_id)
    validate_and_save(form)


@login_required
def update_client(request: WSGIRequest, client_id: int):
    client_to_edit = get_object_or_404(Client, pk=client_id)
    if request.method == 'POST':
        try:
            update_client_util(ClientForm(request.POST, instance=client_to_edit), client_id)
            return redirect('clients:clients')
        except ValueError as e:
            return render(request, 'clients/add_client.html',
                          {'form': ClientForm(request.POST), 'error': e})
    else:
        form = ClientForm(instance=client_to_edit)
    return render(request, 'clients/add_client.html', {'form': form, 'client': client_to_edit})


@api_view(['PATCH'])
def update_client_api(request, client_id: int):
    client_to_edit = get_object_or_404(Client, pk=client_id)
    try:
        old_data = ClientSerializer(client_to_edit).data
        new_data = {**old_data, **request.data}
        update_client_util(ClientForm(new_data, instance=client_to_edit), client_id)
    except ValueError as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    return Response(status=status.HTTP_200_OK)


# delete client

def delete_client_util(client: Client):
    client.delete()


@login_required
def delete_client(request, client_id: int):
    client = get_object_or_404(Client, pk=client_id)
    try:
        delete_client_util(client)
    except Exception as e:
        return render(request, 'clients/clients.html', {'error': str(e)})
    return redirect('clients:clients')


@api_view(['DELETE'])
def delete_client_api(request, client_id: int):
    client = get_object_or_404(Client, pk=client_id)
    try:
        delete_client_util(client)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_404_NOT_FOUND)
    return Response(status=status.HTTP_200_OK)


def validate_and_save(form: ClientForm) -> Client:
    if not form.is_valid():
        raise ValueError(form.errors)
    new_client = form.save(commit=False)
    phone_str = str(new_client.phone_number)
    if len(phone_str) != 10:
        raise ValueError("Неверный номер телефона")

    operator_code = int(phone_str[:3])
    new_client.operator_code = operator_code
    new_client.phone_number = int('7' + phone_str)
    new_client.save()
    return new_client
