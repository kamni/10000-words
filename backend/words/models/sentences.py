import pathlib
import uuid

from django.contrib.auth.models import User
from django.db import models
from django.utils.translation import gettext_lazy as _

from .words import Word
from ..utils.audio import get_audio_upload_path
from ..utils.languages import language_choices


def sentence_directory_path(instance: models.Model, filename:str):
    """
    Where to upload audio files for sentences

    See https://docs.djangoproject.com/en/5.1/ref/models/fields/#filefield
    """

    filename = get_audio_upload_path(
        instance.user.id,
        uuid.uuid4(),
        instance.language,
    )
    return filename


class Sentence(models.Model):
    """
    Sentence from an uploaded document.
    """

    class Meta:
        unique_together = [['user', 'language', 'text']]

    id = models.UUIDField(
        primary_key=True,
        blank=True,
        editable=False,
        default=uuid.uuid4,
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        help_text=_('User who uploaded this sentence'),
    )
    language = models.CharField(
        max_length=8,
        choices=language_choices(),
        help_text=_('Language that the sentence belongs to'),
    )
    text = models.TextField()
    audio_file = models.FileField(
        upload_to=sentence_directory_path,
        blank=True,
        null=True,
    )
    translations = models.ManyToManyField(
        'self',
        symmetrical=True,
        help_text=_('Sentences in other language that mean the same or similar'),
    )

    def __str__(self):
        return self.text

    def delete(self):
        if self.audio_file.name:
            audio_file = pathlib.Path(self.audio_file.name)
            if audio_file.exists():
                audio_file.unlink()
        super().delete()


class WordOrder(models.Model):
    """
    Join table to keep track of word order in a sentence
    """

    class Meta:
        ordering = ['sentence', 'order']
        unique_together = [['word', 'sentence', 'order']]
        verbose_name_plural = 'Word order'

    word = models.ForeignKey(
        Word,
        on_delete=models.CASCADE,
    )
    sentence = models.ForeignKey(
        Sentence,
        on_delete=models.CASCADE,
    )
    order = models.PositiveIntegerField()
