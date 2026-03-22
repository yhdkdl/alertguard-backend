from rest_framework import generics, permissions, status
from rest_framework.response import Response
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

        data            = serializer.validated_data
        idempotency_key = data.get('idempotency_key')

        # ── Idempotency check ──────────────────────────────────────
        # If we already processed this exact alert, return the original
        # This handles Flutter retrying after a timeout
        if idempotency_key:
            existing = Alert.objects.filter(
                user=request.user,
                idempotency_key=idempotency_key
            ).first()

            if existing:
                print(f'[Idempotency] Duplicate request — '
                      f'returning existing alert id: {existing.id}')
                return Response(
                    AlertResponseSerializer(existing).data,
                    status=status.HTTP_200_OK  # 200 not 201 — not newly created
                )

        # ── Upload photos ──────────────────────────────────────────
        front_photo_url = None
        rear_photo_url  = None

        if data.get('front_photo'):
            front_photo_url = upload_photo(data['front_photo'])

        if data.get('rear_photo'):
            rear_photo_url = upload_photo(data['rear_photo'])

        # ── Save alert ─────────────────────────────────────────────
        alert = Alert.objects.create(
            user=request.user,
            trigger_type=data['trigger_type'],
            latitude=data.get('latitude'),
            longitude=data.get('longitude'),
            front_photo_url=front_photo_url,
            rear_photo_url=rear_photo_url,
            is_test=data.get('is_test', False),
            idempotency_key=idempotency_key,
            status='pending',
        )

        # ── Dispatch Telegram ──────────────────────────────────────
        contacts = request.user.emergency_contacts.all()

        if alert.is_test:
            alert.status = 'sent'
        else:
            dispatched   = dispatch_alert(alert, contacts)
            alert.status = 'sent' if dispatched else 'failed'

        alert.save()

        return Response(
            AlertResponseSerializer(alert).data,
            status=status.HTTP_201_CREATED
        )


class AlertListView(generics.ListAPIView):
    serializer_class   = AlertResponseSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Alert.objects.filter(user=self.request.user)