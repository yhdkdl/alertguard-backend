from rest_framework import generics, permissions, status
from rest_framework.response import Response

from apps import contacts
from .models import Alert
from .serializers import AlertCreateSerializer, AlertResponseSerializer
from .services.cloudinary_service import upload_photo
from .services.telegram_service import dispatch_alert


class AlertCreateView(generics.CreateAPIView):
    serializer_class   = AlertCreateSerializer
    permission_classes = [permissions.IsAuthenticated]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        data = serializer.validated_data

        # 1. Upload photos to Cloudinary (each independently)
        front_photo_url = None
        rear_photo_url  = None

        if data.get('front_photo'):
            front_photo_url = upload_photo(data['front_photo'])

        if data.get('rear_photo'):
            rear_photo_url = upload_photo(data['rear_photo'])

        # 2. Save the alert to the database with status 'pending'
        alert = Alert.objects.create(
            user=request.user,
            trigger_type=data['trigger_type'],
            latitude=data.get('latitude'),
            longitude=data.get('longitude'),
            front_photo_url=front_photo_url,
            rear_photo_url=rear_photo_url,
            is_test=data.get('is_test', False),
            status='pending',
        )

        # 3. Get contacts to notify
        contacts = request.user.emergency_contacts.all()
             
            
        # 4. In test mode, only notify the user themselves
        if alert.is_test:
            from apps.contacts.models import EmergencyContact
            # Create a temporary fake contact using the user's own telegram info
            # (handled in telegram_service by checking is_test on alert)
            dispatched = False
        else:
            dispatched = dispatch_alert(alert, contacts)

        # 5. Update alert status based on dispatch result
        if alert.is_test:
            alert.status = 'sent'
        elif dispatched:
            alert.status = 'sent'
        else:
            alert.status = 'failed'
            

        alert.save()

        # 6. Return the alert using the response serializer
        response_serializer = AlertResponseSerializer(alert)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)


class AlertListView(generics.ListAPIView):
    serializer_class   = AlertResponseSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Alert.objects.filter(user=self.request.user)