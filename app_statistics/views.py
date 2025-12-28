from django.shortcuts import render
from django.http import HttpResponse
import requests
import os
import json


STATS_API_URL = os.getenv("STATISTICS_API_URL", "http://localhost:8080")

def statistics(request):
    return HttpResponse(content="this page is currently unavailable")

def dataframe_info(request):
    data = requests.get(f'{STATS_API_URL}/info')
    data_dict = json.loads(data.content)
    return render(request, "pd_info.html", data_dict)