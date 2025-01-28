"""
Copyright (C) J Leadbetter <j@jleadbetter.com>
Affero GPL v3
"""

import pathlib
import uuid

from django.contrib.auth.models import User
from django.db import models
from django.utils.translation import gettext_lazy as _

from common.models.users import DocumentBase
from common.utils.files import document_upload_path

from ..utils.languages import language_code_choices


class Document(DocumentBase, models.Model):
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
        upload_to=document_upload_path,
        help_text=_('Uploaded document'),
    )
    translations = models.ManytoManyField(
        'Document',
        symmetrical=True,
        help_text=_('Other language translations of this document'),
    )


    def __str__(self):
        return self.display_name
