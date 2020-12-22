"""Bunny urls"""
from django.urls import path

from bunny import views

urlpatterns = [
    path("<str:input_query>/", views.query, name="query"),
    path("", views.query, name="query")
    # path('', views.index, name="index"),
]
