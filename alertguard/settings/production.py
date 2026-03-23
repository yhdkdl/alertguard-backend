import os
import dj_database_url
from .base import *

# Security
DEBUG        = False
SECRET_KEY   = os.environ.get('SECRET_KEY')
ALLOWED_HOSTS = [
    os.environ.get('RENDER_EXTERNAL_HOSTNAME', ''),
    'alertguard-api.onrender.com',
]

# Production database — Supabase PostgreSQL
DATABASES = {
    'default': dj_database_url.config(
        default=os.environ.get('DATABASE_URL'),
        conn_max_age=600,
        conn_health_checks=True,
    )
}

# Static files served by WhiteNoise
STATICFILES_STORAGE = (
    'whitenoise.storage.CompressedManifestStaticFilesStorage'
)

# Security headers
SECURE_BROWSER_XSS_FILTER      = True
SECURE_CONTENT_TYPE_NOSNIFF    = True
X_FRAME_OPTIONS                = 'DENY'
SECURE_SSL_REDIRECT            = True
SESSION_COOKIE_SECURE          = True
CSRF_COOKIE_SECURE             = True

# CORS — allows Flutter app to call the API
CORS_ALLOWED_ORIGINS = [
    'https://alertguard-api.onrender.com',
]
CORS_ALLOW_ALL_ORIGINS = True  # simplify for MVP