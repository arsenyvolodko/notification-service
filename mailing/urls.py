from django.urls import path

from mailing import views

app_name = 'mailing'

urlpatterns = [
    path("", views.mailing, name="mailing"),
    path('create_mailing/', views.create_mailing, name='create_mailing'),
    path('update_mailing/<int:mailing_id>', views.update_mailing, name='update_mailing'),
    path('delete_mailing/<int:mailing_id>', views.delete_mailing, name='delete_mailing'),

    path('create/', views.create_mailing_api, name='create_mailing_api'),
    path('delete/<int:mailing_id>', views.delete_mailing_api, name='delete_mailing_api'),
    path('update/<int:mailing_id>', views.update_mailing_api, name='update_mailing_api'),
]
