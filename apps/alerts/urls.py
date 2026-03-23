from django.urls import path
from .views import AlertCreateView, AlertListView

urlpatterns = [
    path('',    AlertCreateView.as_view(), name='alert-create'),
    path('history/', AlertListView.as_view(), name='alert-history'),
]