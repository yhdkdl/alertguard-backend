import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from apps.contacts.models import EmergencyContact


@csrf_exempt
@require_POST
def telegram_webhook(request):
    """
    Telegram sends a POST request here every time someone
    messages the bot. We parse the payload and handle
    /start verify_<token> commands.
    """
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({'error': 'invalid JSON'}, status=400)

    message = data.get('message', {})
    if not message:
        # Telegram sends other update types (edited messages etc.)
        # We only care about new messages
        return JsonResponse({'ok': True})

    chat_id = message.get('chat', {}).get('id')
    text    = message.get('text', '')

    if not chat_id or not text:
        return JsonResponse({'ok': True})

    # Handle /start verify_<token>
    if text.startswith('/start verify_'):
        token = text.replace('/start verify_', '').strip()
        _handle_verification(chat_id, token)

    elif text.startswith('/start'):
        # Someone opened the bot without a token
        # (e.g. searched for it manually)
        _send_welcome_message(chat_id)

    return JsonResponse({'ok': True})


def _handle_verification(chat_id: int, token: str):
    """
    Find the contact by invite_token, save their Chat ID,
    mark them as verified, and send a confirmation message.
    """
    try:
        contact = EmergencyContact.objects.get(invite_token=token)

        if contact.telegram_verified:
            _send_message(
                chat_id,
                "✅ You are already verified as an emergency contact."
            )
            return

        # Save the real Chat ID and mark as verified
        contact.telegram_id       = str(chat_id)
        contact.telegram_verified = True
        contact.save()

        _send_message(
            chat_id,
            f"✅ *Verification successful!*\n\n"
            f"You are now registered as an emergency contact for "
            f"*{contact.user.full_name}* on AlertGuard.\n\n"
            f"If they send an SOS alert, you will be notified here immediately."
        )

    except EmergencyContact.DoesNotExist:
        _send_message(
            chat_id,
            "❌ This invite link is invalid or has expired. "
            "Please ask your contact to share a new link."
        )


def _send_welcome_message(chat_id: int):
    _send_message(
        chat_id,
        "👋 Welcome to *AlertGuard Bot*.\n\n"
        "This bot notifies you when someone you care about "
        "sends an emergency SOS alert.\n\n"
        "To become an emergency contact, ask the AlertGuard "
        "user to share their invite link with you."
    )


def _send_message(chat_id: int, text: str):
    """
    Send a message back to the user via Telegram.
    Imported here to avoid circular imports.
    """
    from apps.alerts.services.telegram_service import _send_text
    _send_text(str(chat_id), text)