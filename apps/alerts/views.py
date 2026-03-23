from rest_framework import generics, permissions, status
from rest_framework.response import Response
from .models import Alert
from .serializers import AlertCreateSerializer, AlertResponseSerializer
from .services.cloudinary_service import upload_photo
from .services.telegram_service import dispatch_alert, send_alert_to_contact


class AlertCreateView(generics.CreateAPIView):
    serializer_class   = AlertCreateSerializer
    permission_classes = [permissions.IsAuthenticated]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        data            = serializer.validated_data
        idempotency_key = data.get('idempotency_key')

        # ── Idempotency check ──────────────────────────────────
        if idempotency_key:
            existing = Alert.objects.filter(
                user=request.user,
                idempotency_key=idempotency_key,
            ).first()

            if existing:
                print(
                    f'[Idempotency] Returning existing '
                    f'alert id: {existing.id}'
                )
                return Response(
                    AlertResponseSerializer(existing).data,
                    status=status.HTTP_200_OK,
                )

        # ── Upload photos ──────────────────────────────────────
        front_photo_url = None
        rear_photo_url  = None

        if data.get('front_photo'):
            front_photo_url = upload_photo(data['front_photo'])

        if data.get('rear_photo'):
            rear_photo_url = upload_photo(data['rear_photo'])

        # ── Save alert ─────────────────────────────────────────
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

        # ── Dispatch ───────────────────────────────────────────
        if alert.is_test:
            alert.status = _dispatch_test_alert(alert)
        else:
            contacts     = request.user.emergency_contacts.all()
            dispatched   = dispatch_alert(alert, contacts)
            alert.status = 'sent' if dispatched else 'failed'

        alert.save()

        return Response(
            AlertResponseSerializer(alert).data,
            status=status.HTTP_201_CREATED,
        )


def _dispatch_test_alert(alert) -> str:
    """
    Send alert only to the user themselves via their
    verified personal Telegram. Used in Test Mode.
    """
    user = alert.user

    if not user.telegram_verified or not user.telegram_id:
        print(
            f'[TestMode] User {user.email} has not connected '
            f'their Telegram — cannot send test alert'
        )
        return 'failed'

    triggered_at = alert.created_at.strftime("%Y-%m-%d %H:%M UTC")

    success = send_alert_to_contact(
        telegram_id=user.telegram_id,
        user_full_name=user.get_full_name() or user.email,
        latitude=alert.latitude,
        longitude=alert.longitude,
        triggered_at=triggered_at,
        trigger_type=alert.trigger_type + ' (TEST)',
        front_photo_url=alert.front_photo_url,
        rear_photo_url=alert.rear_photo_url,
    )

    if success:
        print(f'[TestMode] Test alert sent to {user.email}')
        return 'sent'

    print(f'[TestMode] Test alert failed for {user.email}')
    return 'failed'


class AlertListView(generics.ListAPIView):
    serializer_class   = AlertResponseSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Alert.objects.filter(user=self.request.user)