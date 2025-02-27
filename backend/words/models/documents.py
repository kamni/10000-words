"""
Copyright (C) J Leadbetter <j@jleadbetter.com>
Affero GPL v3
"""

import pathlib
import uuid

from django.core.serializers.json import DjangoJSONEncoder
from django.db import models
from django.utils.translation import gettext_lazy as _

from common.utils.languages import language_code_choices

from users.models.profile import UserProfile


class Document(models.Model):
    """
    Document with words to study.
    """

    class Meta:
        ordering = ['language_code', 'display_name']
        unique_together = [['user', 'display_name', 'language_code']]

    id = models.UUIDField(
        primary_key=True,
        blank=True,
        editable=False,
        default=uuid.uuid4,
    )
    user = models.ForeignKey(
        UserProfile,
        on_delete=models.CASCADE,
        help_text=_('User who uploaded this document'),
    )
    display_name = models.CharField(
        max_length=255,
        help_text=_('How the document will be named in the UI'),
    )
    language_code = models.CharField(
        max_length=8,
        choices=language_code_choices,
        help_text=_('Language that the document belongs to'),
    )
    attrs = models.JSONField(
        blank=True,
        null=True,
        encoder=DjangoJSONEncoder,
    )

    def __str__(self):
        return self.display_name
