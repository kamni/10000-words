"""
Copyright (C) J Leadbetter <j@jleadbetter.com>
Affero GPL v3
"""
import uuid

from django.contrib.auth.models import User
from django.db import models
from django.utils.translation import gettext_lazy as _


class UserProfile(models.Model):
    """
    Additional information for the django User model.
    Use this instead of the django User model when querying for a User.
    """

    class Meta:
        ordering = ['created']
        verbose_name_plural = 'User Profile'

    id = models.UUIDField(
        primary_key=True,
        blank=True,
        editable=False,
        default=uuid.uuid4,
    )
    created = models.DateTimeField(
        blank=True,
        auto_now_add=True,
        editable=False,
    )
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        help_text=_('Settings belong to this user'),
    )
    display_name = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        help_text=_('Display name shown in the UI'),
    )

    def __str__(self):
        return self.username

    @property
    def is_admin(self):
        return self.user.is_superuser

    @property
    def password(self):
        return self.user.password

    @property
    def username(self):
        return self.user.username
