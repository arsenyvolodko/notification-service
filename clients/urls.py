from django.urls import path

from clients import views

app_name = 'clients'

urlpatterns = [
    path("", views.clients, name="clients"),
    path('create_client/', views.create_client, name='add_client'),
    path('update_client/<int:client_id>', views.update_client, name='update_client'),
    path('delete_client/<int:client_id>', views.delete_client, name='delete_client'),

    path('create/', views.create_client_api, name='create_client_api'),
    path('delete/<int:client_id>', views.delete_client_api, name='delete_client_api'),
    path('update/<int:client_id>', views.update_client_api, name='update_client_api'),
]
