import uuid

from django.contrib.auth.models import User
from django.db import models
from django.utils.translation import gettext_lazy as _

from .words import Conjugation
from ..utils.languages import language_choices


class ProgressTracker(models.Model):
    """
    Tracks user progress with conjugations.

    We're not tracking at the word level,
    because we want to ensure that a user has learned all forms of the word.
    """

    class Status(models.TextChoices):
        """
        Status explanations:

        * learned: The user is comfortable with this word
          and doesn't wish to train on it.

        * currently_learning: The user is currently learning this word.

        * waiting_to_learn: The user has not yet added this word to the
          learning rotation.

        * unknown: The user has not yet created a conjugation for this word.

        * hidden: The user wishes to hide this word from the learning process.
          This is most useful for articles and prepositions,
          because they are hard to learn separately from context.
        """

        learned = _('learned')
        currently_learning = _('currently learning')
        waiting_to_learn = _('waiting to learn')
        hidden = _('hidden')

    class Meta:
        ordering = ['user', 'language', 'status']
        unique_together = [['user', 'conjugation']]

    id = models.UUIDField(
        primary_key=True,
        blank=True,
        default=uuid.uuid4,
        editable=False,
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        help_text=_('User who is learning this conjugation of a word'),
    )
    # This is on the conjugation,
    # but we're putting this here for normalization
    language = models.CharField(
        max_length=8,
        choices=language_choices(),
        help_text=_('Language that the word belongs to'),
    )
    conjugation = models.ForeignKey(
        Conjugation,
        on_delete=models.CASCADE,
        help_text=_('Word conjugation to learn'),
    )
    status = models.CharField(
        max_length=20,
        choices=Status,
        blank=True,
        default=Status.waiting_to_learn,
        help_text=_('Current status of user progress'),
    )
