"""
Copyright (C) J Leadbetter <j@jleadbetter.com>
Affero GPL v3
"""

import uuid

from django.db import models
from django.utils.translation import gettext_lazy as _

from common.utils.languages import language_code_choices
from users.models.profile import UserProfile

from .documents import Document


class Sentence(models.Model):
    """
    Sentences that make up a Document.
    """

    class Meta:
        ordering = ['document', 'ordering']
        unique_together = [
            ['user', 'text', 'language_code', 'ordering', 'document'],
        ]

    id = models.UUIDField(
        primary_key=True,
        blank=True,
        editable=False,
        default=uuid.uuid4,
    )
    user = models.ForeignKey(
        UserProfile,
        on_delete=models.CASCADE,
        help_text=_('User who created this sentence'),
    )
    # Translation sentences are not affiliated with a document
    document = models.ForeignKey(
        Document,
        blank=True,
        null=True,
        on_delete=models.CASCADE,
        help_text=_('Document that this sentence belongs to'),
    )
    language_code = models.CharField(
        max_length=8,
        choices=language_code_choices,
        help_text=_('Language that the sentence belongs to'),
    )
    # If no ordering is specified,
    # this is probably a translation.
    ordering = models.PositiveIntegerField(
        blank=True,
        default=0,
        help_text=_('Order that the sentence has in a document'),
    )
    text = models.TextField(
        help_text=_('Text for the sentence in the specified language'),
    )
    enabled_for_study = models.BooleanField(
        blank=True,
        default=False,
        help_text=_('When enabled, shows up in learning sections of the app'),
    )

    translation_of = models.ForeignKey(
        'Sentence',
        blank=True,
        null=True,
        on_delete=models.CASCADE,
        related_name='translation_set',
        help_text=_('This sentence is a translation of another sentence'),
    )
