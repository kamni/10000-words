"""
Copyright (C) J Leadbetter <j@jleadbetter.com>
Affero GPL v3
"""

import pathlib
import uuid

from django.contrib.auth.models import User
from django.db import models
from django.utils.translation import gettext_lazy as _

from ..utils.audio import get_audio_upload_path
from ..utils.languages import language_choices


def word_directory_path(instance: models.Model, filename:str):
    """
    Where to upload audio files for words

    See https://docs.djangoproject.com/en/5.1/ref/models/fields/#filefield
    """

    filename = get_audio_upload_path(
        instance.user.id,
        uuid.uuid4(),
        instance.language,
    )
    return filename


class Word(models.Model):
    """
    Word imported from a Document by a User.
    """

    class PartOfSpeechType(models.TextChoices):
        """
        Grammatical part of speech.

        NOTES:

        * Articles are not included here.
          They should be included as part of a noun.

        * Prepositions are not included here,
          because they don't translate well between languages.
          They should be paired with either a verb or an expression.

        * Expressions are for multiple words that mean something different
          than their individual words, and are normally learned together.
          Examples: 'Merry Christmas' and 'It's raining cats and dogs'

        * The 'unknown' type is used for newly imported words,
          until the user sets the type.
        """

        unknown = _('unknown')
        noun = 'noun'
        pronoun = _('pronoun')
        adjective = _('adjective')
        adverb = _('adverb')
        verb = _('verb')
        participle = _('participle')
        conjunction = _('conjunction')
        expression = _('expression')

    class Meta:
        ordering = ['user']
        unique_together = [('user', 'language', 'root_word')]

    id = models.UUIDField(
        primary_key=True,
        blank=True,
        default=uuid.uuid4,
        editable=False,
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        help_text=_('User who uploaded this word'),
    )
    language = models.CharField(
        max_length=8,
        choices=language_choices(),
        help_text=_('Language that the word belongs to'),
    )
    type = models.CharField(
        max_length=20,
        choices=PartOfSpeechType,
        help_text=_(
            'The word type, i.e., the grammatical part of speech. '
            'Articles and prepositions should be added to either a noun, '
            'verb, or expression, because they rarely make sense on their '
            'own.'
        ),
    )
    root_word = models.CharField(
        max_length=100,
        help_text=_('The base root word in the language'),
    )
    audio_file = models.FileField(
        upload_to=word_directory_path,
        blank=True,
        null=True,
    )
    translations = models.ManyToManyField(
        'self',
        symmetrical=True,
        help_text=_('Words in other language that mean the same or similar'),
    )

    def __str__(self):
        return self.root_word

    def delete(self):
        if self.audio_file.name:
            audio_file = pathlib.Path(self.audio_file.name)
            if audio_file.exists():
                audio_file.unlink()
        super().delete()


class Conjugation(models.Model):
    """
    Variation of a word.
    Depending on the language, not all fields are necessary.

    Example: In English, words like 'apple' don't have gender.
    But it does have a plural ('apples'),
    and uses 'an' for singular,
    and 'the' for both singular and plural.
    """

    class Case(models.TextChoices):
        nominative = _('nominative')
        accusative = _('accusative')
        dative = _('dative')
        genitive = _('genitive')

    class Person(models.TextChoices):
        first = _('first')
        second = _('second')
        third = _('third')

    class Plurality(models.TextChoices):
        single = _('single')
        plural = _('plural')

    class Gender(models.TextChoices):
        neutral = _('neutral')
        feminine = _('feminine')
        masculine = _('masculine')

    class Politeness(models.TextChoices):
        casual = _('casual')
        formal = _('formal')

    class Emphasis(models.TextChoices):
        stressed = _('stressed')
        unstressed = _('unstressed')

    class Meta:
        unique_together = [['user', 'language', 'text']]

    id = models.UUIDField(
        primary_key=True,
        blank=True,
        default=uuid.uuid4,
        editable=False,
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        editable=False,
        help_text=_('User who uploaded this conjugation'),
    )
    word = models.ForeignKey(
        Word,
        on_delete=models.CASCADE,
    )
    language = models.CharField(
        max_length=8,
        choices=language_choices(),
        editable=False,
        help_text=_('Language that the word belongs to'),
    )
    text = models.CharField(
        max_length=255,
        help_text=_('Text of the conjugated word'),
    )
    examples = models.ManyToManyField(
        'Sentence',
        symmetrical=True,
        help_text=_('Sentence examples for this word'),
    )
    article = models.CharField(
        max_length=40,
        blank=True,
        null=True,
    )
    case = models.CharField(
        max_length=40,
        blank=True,
        null=True,
        choices=Case,
    )
    gender = models.CharField(
        max_length=40,
        blank=True,
        null=True,
        choices=Gender,
    )
    plurality = models.CharField(
        max_length=40,
        blank=True,
        null=True,
        choices=Plurality,
    )
    politeness = models.CharField(
        max_length=40,
        blank=True,
        null=True,
        choices=Politeness,
    )
    tense = models.CharField(
        max_length=40,
        blank=True,
        null=True,
    )
    emphasis = models.CharField(
        max_length=40,
        blank=True,
        null=True,
        choices=Emphasis,
    )

    def __str__(self):
        return self.text
