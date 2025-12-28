from django.urls import path
from . import views

app_name = "app_statistics"

urlpatterns = [
    path('', views.statistics, name='statistics'),
    path('info', views.dataframe_info, name='pd_info'),
]
