"""
Copyright (C) J Leadbetter <j@jleadbetter.com>
Affero GPL v3
"""

import pathlib
import uuid

from django.contrib.auth.models import User
from django.db import models
from django.utils.translation import gettext_lazy as _

from ..utils.languages import language_code_choices


def document_directory_path(instance: models.Model, filename:str):
    """
    Where to upload documents

    See https://docs.djangoproject.com/en/5.1/ref/models/fields/#filefield
    """

    return f'uploads/{instance.user.id}/{instance.language}/docs/{filename}'


class Document(models.Model):
    """
    Uploaded document with words to study.
    """

    class Meta:
        unique_together = [['user', 'display_name', 'language']]

    id = models.UUIDField(
        primary_key=True,
        blank=True,
        editable=False,
        default=uuid.uuid4,
    )
    user = models.ForeignKey(
        User,
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
    doc_file = models.FileField(
        upload_to=document_directory_path,
        unique=True,
    )

    def __str__(self):
        return self.display_name
