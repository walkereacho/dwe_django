"""Django admin portal"""
from django.contrib import admin

from bunny.models import BunnyRedirect

admin.site.register(BunnyRedirect)
