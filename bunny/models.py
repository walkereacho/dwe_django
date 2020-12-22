"""Bunny Models"""
from django.db import models


class BunnyRedirect(models.Model):
    """Bunny Redirect types - model for a redirecting url"""
    key = models.CharField(max_length=20)
    no_arg_return = models.CharField(max_length=100)
    arg_return = models.CharField(max_length=100)

    def __str__(self):
        return self.key
