from django.urls import path

from stats import views

app_name = 'stats'

urlpatterns = [
    path('', views.get_common_stats_api, name='get_common_stats_api'),
    path('<int:mailing_id>', views.get_spec_stats_api, name='get_spec_stats_api'),
]
