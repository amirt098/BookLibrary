import os
from django.contrib import admin
from django.urls import path, include, re_path
from django.conf import settings
from django.views.static import serve

DJANGO_ADMIN_PATH = os.getenv('DJANGO_ADMIN_PATH')
urlpatterns = [
    path('notifier/',include('apps.notifier.urls')),
    path(DJANGO_ADMIN_PATH + '/', admin.site.urls),
    re_path(r'^media/(?P<path>.*)$', serve, {'document_root': settings.MEDIA_ROOT}),
]

