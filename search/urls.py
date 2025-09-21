from django.urls import path
from .views import *

app_name = 'search'

urlpatterns = [
    path("preview/", search_preview, name="search_preview"),
    path("result/", search_result_page, name="search_result"),
]