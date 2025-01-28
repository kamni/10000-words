import string

from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import Conjugation, Document, LearningTracker
from .utils.audio import download_audio
from .utils.documents import create_sentences_and_words


@receiver(post_save, sender=Document)
def process_document(sender, **kwargs):
    """
    After a document is uploaded, create the Sentences and Words
    """

    instance = kwargs.get('instance')
    created = kwargs.get('created')
    if instance and created:
        create_sentences_and_words(instance)


@receiver(post_save, sender=Conjugation)
def create_audio_file_and_tracker(sender, **kwargs):
    """
    After a Conjugation is created, create a new LearningTracker
    """

    instance = kwargs.get('instance')
    created = kwargs.get('created')
    if instance and created:
        LearningTracker.objects.create(
            user=instance.user,
            language=instance.language,
            conjugation=instance,
        )

        audio_file = download_audio(
            user_id=insstance.user.id,
            text_id=instance.id,
            text=instance.text,
            language_code=instance.language,
        )
        instance.audio_file.name = audio_file
        instance.save()
