from django.urls import path
from .views import EmergencyContactListCreateView, EmergencyContactDetailView

urlpatterns = [
    path('', EmergencyContactListCreateView.as_view(), name='contact-list-create'),
    path('<int:pk>/', EmergencyContactDetailView.as_view(), name='contact-detail'),
]