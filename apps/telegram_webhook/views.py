import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from apps.contacts.models import EmergencyContact


@csrf_exempt
@require_POST
def telegram_webhook(request):
    """
    Receives all Telegram bot updates.
    Routes /start commands to either user or contact verification.
    """
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({'error': 'invalid JSON'}, status=400)

    message = data.get('message', {})
    if not message:
        # Non-message update (edit, reaction, etc.) — ignore
        return JsonResponse({'ok': True})

    chat_id = message.get('chat', {}).get('id')
    text    = message.get('text', '')

    if not chat_id or not text:
        return JsonResponse({'ok': True})

    # Route based on token prefix
    if text.startswith('/start verify_user_'):
        token = text.replace('/start verify_user_', '').strip()
        _handle_user_verification(chat_id, token)

    elif text.startswith('/start verify_'):
        token = text.replace('/start verify_', '').strip()
        _handle_contact_verification(chat_id, token)

    elif text.startswith('/start'):
        _send_welcome_message(chat_id)

    # Always return 200 — Telegram retries on any other status
    return JsonResponse({'ok': True})


def _handle_user_verification(chat_id: int, token: str):
    """
    User clicks their own invite link from Settings.
    Connects their personal Telegram for Test Mode.
    """
    from django.contrib.auth import get_user_model
    User = get_user_model()

    try:
        user = User.objects.get(invite_token=token)

        if user.telegram_verified:
            _send_message(
                chat_id,
                "✅ Your Telegram is already connected to AlertGuard.\n\n"
                "You can use Test Mode in the app to verify "
                "your SOS alerts reach you."
            )
            return

        # Save chat_id and mark verified
        user.telegram_id       = str(chat_id)
        user.telegram_verified = True
        user.save()

        print(
            f'[Webhook] User {user.email} connected '
            f'Telegram chat_id: {chat_id}'
        )

        _send_message(
            chat_id,
            f"✅ *Telegram connected successfully!*\n\n"
            f"Hi *{user.full_name}*, your Telegram account is "
            f"now linked to your AlertGuard profile.\n\n"
            f"🧪 *Test Mode:* When you enable Test Mode in the "
            f"app and trigger an SOS, the alert will be sent "
            f"here so you can verify everything works.\n\n"
            f"🚨 *Real alerts* will go to your emergency "
            f"contacts — not here.\n\n"
            f"You are all set! 🛡️"
        )

    except User.DoesNotExist:
        _send_message(
            chat_id,
            "❌ This link is invalid or has expired.\n\n"
            "Please open AlertGuard → Settings → "
            "Connect My Telegram to get a new link."
        )


def _handle_contact_verification(chat_id: int, token: str):
    """
    Emergency contact clicks invite link shared by user.
    Connects their Telegram to receive real SOS alerts.
    """
    try:
        contact = EmergencyContact.objects.get(invite_token=token)

        if contact.telegram_verified:
            _send_message(
                chat_id,
                "✅ You are already verified as an emergency "
                "contact for "
                f"*{contact.user.full_name}*."
            )
            return

        contact.telegram_id       = str(chat_id)
        contact.telegram_verified = True
        contact.save()

        print(
            f'[Webhook] Contact {contact.name} verified '
            f'for user {contact.user.email}'
        )

        _send_message(
            chat_id,
            f"✅ *Verification successful!*\n\n"
            f"You are now registered as an emergency contact "
            f"for *{contact.user.full_name}* on AlertGuard.\n\n"
            f"🚨 If they trigger an SOS alert, you will "
            f"receive an immediate notification here with "
            f"their location and photos.\n\n"
            f"Thank you for being there for them. 🙏"
        )

    except EmergencyContact.DoesNotExist:
        _send_message(
            chat_id,
            "❌ This invite link is invalid or has expired.\n\n"
            "Please ask your contact to share a new link "
            "from their AlertGuard app."
        )


def _send_welcome_message(chat_id: int):
    _send_message(
        chat_id,
        "👋 Welcome to *AlertGuard Bot*.\n\n"
        "This bot sends emergency SOS alerts to your loved ones.\n\n"
        "📱 *Are you an AlertGuard user?*\n"
        "Open the app → Settings → Connect My Telegram\n\n"
        "👥 *Are you an emergency contact?*\n"
        "Ask the AlertGuard user to share their contact "
        "invite link with you."
    )


def _send_message(chat_id: int, text: str):
    from apps.alerts.services.telegram_service import _send_text
    _send_text(str(chat_id), text)