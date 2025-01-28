"""
Copyright (C) J Leadbetter <j@jleadbetter.com>
Affero GPL v3
"""

import pathlib
import uuid

from django.contrib.auth.models import User
from django.db import models
from django.utils.translation import gettext_lazy as _

from .sentences import Sentence, WordOrder
from .words import Conjugation, Word
from ..utils.languages import language_choices


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
        choices=language_choices(),
        help_text=_('Language that the sentence belongs to'),
    )
    doc_file = models.FileField(
        upload_to=document_directory_path,
        unique=True,
    )

    def __str__(self):
        return self.display_name

    def delete(self):
        sentence_order = SentenceOrder.objects.filter(document=self)
        sentence_ids = [obj.sentence.id for obj in sentence_order]
        sentence_ids_to_ignore = [
            obj.sentence.id for obj in SentenceOrder.objects.filter(
                sentence__id__in=sentence_ids,
            ).exclude(document=self)
        ]
        sentence_ids_to_delete = list(
            set(sentence_ids).difference(set(sentence_ids_to_ignore)),
        )
        sentences_to_delete = Sentence.objects.filter(
            id__in=sentence_ids_to_delete,
        )

        all_words_to_delete = []
        for sentence in sentences_to_delete:
            word_order = WordOrder.objects.filter(sentence=sentence)
            word_ids = [obj.word.id for obj in word_order]
            word_ids_to_ignore = [
                obj.word.id for obj in WordOrder.objects.filter(
                    word__id__in=word_ids,
                ).exclude(
                    sentence__id__in=sentences_to_delete,
                )
            ]
            word_ids_to_delete = list(
                set(word_ids).difference(set(word_ids_to_ignore)),
            )
            words_to_delete = Word.objects.filter(
                id__in=word_ids_to_delete,
            )
            all_words_to_delete.extend(words_to_delete)

        # Remove duplicates
        all_words_to_delete = list(set(all_words_to_delete))

        # We're not calling a query batch delete,
        # because we need to delete the uploaded files
        # (as handled by word.delete and sentence.delete)
        for word in all_words_to_delete:
            word.delete()
        for sentence in sentences_to_delete:
            sentence.delete()

        doc_file = pathlib.Path(self.doc_file.name)
        if doc_file.exists():
            doc_file.unlink()
        super().delete()


class SentenceOrder(models.Model):
    """
    Join table to keep track of sentence order in a document
    """

    class Meta:
        ordering = ['document', 'order']
        unique_together = [['sentence', 'document', 'order']]
        verbose_name_plural = 'Sentence order'

    sentence = models.ForeignKey(
        Sentence,
        on_delete=models.CASCADE,
    )
    document = models.ForeignKey(
        Document,
        on_delete=models.CASCADE,
    )
    order = models.PositiveIntegerField()
