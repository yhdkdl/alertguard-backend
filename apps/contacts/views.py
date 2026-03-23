from rest_framework import generics, permissions
from .models import EmergencyContact
from .serializers import EmergencyContactSerializer


class EmergencyContactListCreateView(generics.ListCreateAPIView):
    serializer_class   = EmergencyContactSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # Only return contacts belonging to the logged-in user
        return EmergencyContact.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        # Automatically attach the logged-in user on save
        serializer.save(user=self.request.user)


class EmergencyContactDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class   = EmergencyContactSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # A user can only access their own contacts
        return EmergencyContact.objects.filter(user=self.request.user)