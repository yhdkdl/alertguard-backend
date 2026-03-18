from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/v1/auth/', include('apps.users.urls')),
     path('api/v1/contacts/', include('apps.contacts.urls')),
     path('api/v1/alerts/', include('apps.alerts.urls')),
      path('api/v1/webhook/telegram/',  include('apps.telegram_webhook.urls')),
]