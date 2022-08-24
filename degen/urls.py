"""Bunny urls"""
from django.urls import path

from degen import views

urlpatterns = [
    path("", views.degen, name="degen"),
]
