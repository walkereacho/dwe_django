"""Bunny urls"""
from django.urls import path

from baseball import views

urlpatterns = [
    path("", views.baseball, name="baseball"),
]
