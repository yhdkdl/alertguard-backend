# AlertGuard — Backend API

> Production-ready Django REST API powering the AlertGuard emergency safety application.

**Live API:** `https://alertguard-api.onrender.com`  
**Health Check:** `https://alertguard-api.onrender.com/health/`

---

## Overview

AlertGuard is a mobile emergency safety system that allows users to send
instant SOS alerts — with GPS location and camera photos — to verified
emergency contacts via Telegram.

This repository contains the backend API built with Django REST Framework,
deployed on Render with a Supabase PostgreSQL database.

---

## Tech Stack

| Layer       | Technology                          |
|-------------|-------------------------------------|
| Framework   | Django 4.2 + Django REST Framework  |
| Database    | PostgreSQL (Supabase)               |
| Auth        | JWT (djangorestframework-simplejwt) |
| Media       | Cloudinary                          |
| Messaging   | Telegram Bot API                    |
| Deployment  | Render                              |
| Language    | Python 3.11                         |

---

## Architecture
```
Flutter App
    │
    │  HTTPS / REST
    ▼
Django REST API (Render)
    │
    ├── Auth endpoints         JWT register / login / refresh
    ├── Contacts endpoints     CRUD + Telegram invite link generation
    ├── Alerts endpoints       SOS trigger + Cloudinary upload
    └── Telegram webhook       Contact + user verification
    │
    ├── Supabase PostgreSQL    Persistent data store
    ├── Cloudinary             Photo storage
    └── Telegram Bot API       Alert delivery
```

---

## Features

### Authentication
- Email-based custom user model
- JWT access + refresh tokens
- Token auto-refresh on expiry

### Emergency Contacts
- Store up to 3 emergency contacts
- Telegram verification via invite link
- Webhook-based Chat ID capture
- Server-side ownership enforcement

### SOS Alerts
- GPS coordinates captured at trigger time
- Front and rear camera photos uploaded to Cloudinary
- Telegram message dispatch with Google Maps link
- Idempotency key prevents duplicate alerts on retry
- Alert history with full metadata

### Offline Support
- Alerts queued locally when internet unavailable
- Automatic retry on connectivity restore
- Maximum 5 retry attempts before pruning

### Test Mode
- Full SOS drill without notifying real contacts
- Alert sent only to user's own verified Telegram
- Same verification flow as emergency contacts

### Telegram Bot
- Dual verification routing:
  - `/start verify_<token>` — contact verification
  - `/start verify_user_<token>` — user self-verification
- Webhook processes all bot interactions

---

## API Endpoints

### Auth
```
POST   /api/v1/auth/register/          Register new user
POST   /api/v1/auth/login/             Login, receive JWT tokens
POST   /api/v1/auth/token/refresh/     Refresh access token
GET    /api/v1/auth/profile/           Get user profile
PATCH  /api/v1/auth/profile/           Update profile
```

### Contacts
```
GET    /api/v1/contacts/               List user's contacts
POST   /api/v1/contacts/               Add contact (max 3)
GET    /api/v1/contacts/{id}/          Get contact detail
PATCH  /api/v1/contacts/{id}/          Update contact
DELETE /api/v1/contacts/{id}/          Delete contact
```

### Alerts
```
POST   /api/v1/alerts/                 Trigger SOS alert
GET    /api/v1/alerts/history/         Get alert history
```

### System
```
POST   /api/v1/webhook/telegram/       Telegram bot webhook
GET    /health/                        Health check
```

---

## Data Models

### User
```python
email             EmailField (unique, used for auth)
full_name         CharField
telegram_id       CharField (set by webhook)
telegram_verified BooleanField
invite_token      UUIDField (unique, for self-verification)
```

### EmergencyContact
```python
user              ForeignKey(User)
name              CharField
phone_number      CharField
relationship      CharField (choices)
telegram_id       CharField (set by webhook)
telegram_verified BooleanField
invite_token      UUIDField (unique per contact)
```

### Alert
```python
user              ForeignKey(User)
trigger_type      CharField (volume_button | shake | manual)
latitude          DecimalField
longitude         DecimalField
front_photo_url   URLField (Cloudinary)
rear_photo_url    URLField (Cloudinary)
status            CharField (pending | sent | failed)
is_test           BooleanField
idempotency_key   CharField (unique per user)
created_at        DateTimeField
```

---

## Alert Flow
```
Flutter triggers SOS
    │
    ▼
POST /api/v1/alerts/
    │
    ├── Check idempotency key (prevent duplicates)
    ├── Upload front photo → Cloudinary
    ├── Upload rear photo → Cloudinary
    ├── Save alert (status: pending)
    │
    ├── is_test = true?
    │     └── Send to user.telegram_id only
    │
    └── is_test = false?
          └── For each verified contact:
                └── Send Telegram message with:
                      - Google Maps link
                      - Timestamp
                      - Trigger type
                      - Front photo
                      - Rear photo
    │
    └── Update alert status (sent | failed)
```

---

## Telegram Verification Flow
```
User adds contact in app
    │
    ▼
Backend generates invite_token (UUID)
Returns invite_link: https://t.me/bot?start=verify_<token>
    │
    ▼
User shares link to contact
    │
    ▼
Contact clicks link → Telegram opens bot
Bot receives: /start verify_<token>
    │
    ▼
POST /api/v1/webhook/telegram/
Backend finds contact by token
Saves Chat ID → marks telegram_verified = True
Bot sends confirmation message
    │
    ▼
Contact now receives real SOS alerts
```

---

## Local Development Setup

### Prerequisites
- Python 3.11+
- pip

### Installation
```bash
# Clone the repository
git clone https://github.com/YOUR_USERNAME/alertguard-backend.git
cd alertguard-backend

# Create virtual environment
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create environment file
cp .env.example .env
# Edit .env with your values
```

### Environment Variables
```bash
# .env
SECRET_KEY=your-secret-key-min-32-chars
DJANGO_SETTINGS_MODULE=alertguard.settings.local

# Optional for local dev (alerts work without these,
# but photos won't upload and Telegram won't send)
CLOUDINARY_CLOUD_NAME=your_cloud_name
CLOUDINARY_API_KEY=your_api_key
CLOUDINARY_API_SECRET=your_api_secret
TELEGRAM_BOT_TOKEN=your_bot_token
TELEGRAM_BOT_USERNAME=your_bot_username
```

### Run
```bash
python manage.py migrate
python manage.py runserver
```

API is available at `http://localhost:8000`

### Telegram Webhook (Local Development)
```bash
# Install ngrok
ngrok http 8000

# Register webhook
curl "https://api.telegram.org/botYOUR_TOKEN/setWebhook?url=https://YOUR_NGROK_URL/api/v1/webhook/telegram/"
```

---

## Project Structure
```
alertguard-backend/
├── alertguard/
│   ├── settings/
│   │   ├── base.py          Shared settings
│   │   ├── local.py         Development (SQLite)
│   │   └── production.py    Production (PostgreSQL)
│   ├── urls.py
│   └── wsgi.py
├── apps/
│   ├── users/               Auth + user profile
│   ├── contacts/            Emergency contacts + verification
│   ├── alerts/              SOS alert + dispatch
│   │   └── services/
│   │       ├── cloudinary_service.py
│   │       └── telegram_service.py
│   ├── telegram_webhook/    Bot webhook handler
│   └── core/                Health check
├── requirements.txt
├── render.yaml              Render deployment config
└── .env.example
```

---

## Deployment

Deployed on **Render** (free tier) with automatic deploys from the `main` branch.

Every push to `main`:
1. Installs dependencies
2. Collects static files
3. Runs database migrations
4. Restarts the service

### Environment
- **Runtime:** Python 3.11
- **Server:** Gunicorn
- **Database:** Supabase PostgreSQL
- **Media:** Cloudinary
- **Keep-alive:** UptimeRobot (5-minute ping)

---

## Security Highlights

- JWT authentication on all protected endpoints
- User-scoped queries — users can only access their own data
- `telegram_id` set only by verified webhook — never by client
- Idempotency keys prevent duplicate alert delivery
- No secrets committed — all credentials via environment variables
- HTTPS enforced in production

---

## Known Limitations & Roadmap

| Limitation | Planned Fix |
|------------|-------------|
| Telegram only for alerts | SMS + WhatsApp (future sprint) |
| Free tier Render sleeps after inactivity | Paid plan or alternative host |
| No rate limiting on alert endpoint | Add django-ratelimit |
| No email notifications | Add as secondary channel |

---

