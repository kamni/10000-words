"""
Copyright (C) J Leadbetter <j@jleadbetter.com>
Affero GPL v3
"""

from django.db import models
from django.utils.translation import gettext_lazy as _


class AppSettings(models.Model):
    """
    Global settings for apps using this backend.

    WARNING: Highlander Model -- THERE CAN BE ONLY ONE!
    """

    class Meta:
        ordering = ['created']
        verbose_name_plural = 'App Settings'


    created = models.DateTimeField(
        blank=True,
        auto_now_add=True,
        editable=False,
    )
    multiuser_mode = models.BooleanField(
        blank=True,
        default=False,
        help_text=_(
            'Whether app is used by more than one user. '
            'Provides form to add new user, if True.'
        ),
    )
    passwordless_login = models.BooleanField(
        blank=True,
        default=False,
        help_text=_(
           'Whether app requires a password to log on. '
           'If running locally on a computer with trusted users, '
           'then set this to True. '
           'Set False if running as a web server '
           'or local privacy is desired.'
        ),
    )
    show_users_on_login_screen = models.BooleanField(
        blank=True,
        default=False,
        help_text=_(
           'Show or hide the available users. '
           'If running in single-user mode with passwordless login, '
           'set this to True. '
           'If running on the web or with untrusted users, '
           'set this to False.'
        ),
    )
