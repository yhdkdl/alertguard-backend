import requests
from django.conf import settings


TELEGRAM_API = "https://api.telegram.org/bot{token}/{method}"


def _api_url(method: str) -> str:
    return TELEGRAM_API.format(token=settings.TELEGRAM_BOT_TOKEN, method=method)


def send_alert_to_contact(
    telegram_id: str,
    user_full_name: str,
    latitude,
    longitude,
    triggered_at: str,
    trigger_type: str,
    front_photo_url,
    rear_photo_url,
) -> bool:
    maps_link = None
    if latitude and longitude:
        maps_link = f"https://maps.google.com/?q={latitude},{longitude}"

    message = _build_message(
        user_full_name, maps_link, triggered_at, trigger_type
    )

    _send_photos(telegram_id, front_photo_url, rear_photo_url)
    return _send_text(telegram_id, message)


def _build_message(
    full_name: str,
    maps_link,
    triggered_at: str,
    trigger_type: str,
) -> str:
    location_line = (
        f"📍 Location: {maps_link}"
        if maps_link
        else "📍 Location: unavailable"
    )
    return (
        f"🚨 *SOS ALERT*\n"
        f"{full_name} may be in danger.\n\n"
        f"{location_line}\n"
        f"🕐 Time: {triggered_at}\n"
        f"⚡ Trigger: {trigger_type.replace('_', ' ').title()}"
    )


def _send_text(telegram_id: str, message: str) -> bool:
    try:
        response = requests.post(
            _api_url("sendMessage"),
            json={
                "chat_id":    telegram_id,
                "text":       message,
                "parse_mode": "Markdown",
            },
            timeout=10,
        )
        print(f"[Telegram] sendMessage status: {response.status_code}")
        print(f"[Telegram] sendMessage response: {response.json()}")
        return response.status_code == 200
    except Exception as e:
        print(f"[Telegram] sendMessage exception: {e}")
        return False


def _send_photos(telegram_id: str, front_url, rear_url) -> None:
    for label, url in [("front", front_url), ("rear", rear_url)]:
        if not url:
            print(f"[Telegram] skipping {label} photo — no URL")
            continue
        try:
            r = requests.post(
                _api_url("sendPhoto"),
                json={"chat_id": telegram_id, "photo": url},
                timeout=10,
            )
            print(f"[Telegram] sendPhoto ({label}) status: {r.status_code}")
        except Exception as e:
            print(f"[Telegram] sendPhoto ({label}) exception: {e}")


def dispatch_alert(alert, contacts) -> bool:
    triggered_at = alert.created_at.strftime("%Y-%m-%d %H:%M UTC")
    any_success  = False

    print(f"[Telegram] dispatch_alert called")
    print(f"[Telegram] token loaded: {'YES' if settings.TELEGRAM_BOT_TOKEN else 'NO — TOKEN MISSING'}")

    for contact in contacts:
        print(f"[Telegram] processing contact: {contact.name} | telegram_id: '{contact.telegram_id}'")

        if not contact.telegram_id:
            print(f"[Telegram] skipping — no telegram_id")
            continue

        try:
            success = send_alert_to_contact(
                telegram_id=str(contact.telegram_id),
                user_full_name=alert.user.get_full_name() or alert.user.email,
                latitude=alert.latitude,
                longitude=alert.longitude,
                triggered_at=triggered_at,
                trigger_type=alert.trigger_type,
                front_photo_url=alert.front_photo_url,
                rear_photo_url=alert.rear_photo_url,
            )
            print(f"[Telegram] contact {contact.name} — success: {success}")
            if success:
                any_success = True
        except Exception as e:
            print(f"[Telegram] unexpected error for {contact.name}: {e}")

    print(f"[Telegram] dispatch finished — any_success: {any_success}")
    return any_success