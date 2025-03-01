"""
Copyright (C) J Leadbetter <j@jleadbetter.com>
Affero GPL v3
"""

import uuid
from pathlib import Path
from typing import List

from django.core.files import File
from django.db.utils import IntegrityError

from users.models import UserProfile
from words.models import Document, Sentence

from ...models.documents import DocumentDB
from ...models.sentences import SentenceDB
from ...models.errors import ObjectNotFoundError
from ...ports.documents import DocumentDBPort, DocumentUIPort


class DocumentDBDjangoORMAdapter(DocumentDBPort):
    """
    Represents a document in the system
    """

    def __init__(self, **kwargs):
        # Ignore kwargs, as they're not needed
        super().__init__()

    def _django_to_pydantic(self, document: Document) -> DocumentDB:
        # TODO: select_related when we add display_text
        sentences = [
            SentenceDB(
                id=sentence.id,
                user_id=document.user.id,
                document_id=document.id,
                ordering=sentence.ordering,
                language_code=sentence.language_code,
                text=sentence.text,
                enabled_for_study=sentence.enabled_for_study,
            )
            for sentence in document.sentence_set.all()
        ]

        docdb = DocumentDB(
            id=document.id,
            user_id=document.user.id,
            display_name=document.display_name,
            language_code=document.language_code,
            attrs=document.attrs,
            sentences=sentences,
        )
        return docdb

    def create_or_update(self, document: DocumentDB) -> DocumentDB:
        """
        Create a document in the database,
        or update it if it already exists.

        :document: Instance of a DocumentDB to save

        :return: DocumentDB that was created/updated
        :raises: ObjectNotFound error if user does not exist
            or document.sentences contains saved sentences
            that the document does not know about.
        """

        # This raises an ObjectNotFound error.
        # We won't trap it in a try-except block.
        user = UserProfile.objects.get(id=document.user_id)

        if document.id:
            existing_doc = Document.objects.filter(id=document.id).first()
        else:
            existing_doc = Document.objects.filter(
                user__id=document.user_id,
                display_name=document.display_name,
                language_code=document.language_code,
            ).prefetch_related('sentence_set') \
                    .select_related('user').first()

        if existing_doc:
            doc = existing_doc
            doc.display_name = document.display_name
        else:
            doc = Document(
                user=user,
                display_name=document.display_name,
                language_code=document.language_code,
            )

        if document.binary_data:
            doc.attrs = self.parse_binary_data_attrs(document.binary_data)
        else:
            doc.attrs = document.attrs
        # We have to save before we can create sentences
        doc.save()

        if document.binary_data:
            # Sorry, but we're not going to attempt a merge
            Sentence.objects.filter(document=doc).delete()

            sentence_dbs = self.parse_binary_data_sentences(
                document.binary_data,
                doc,
            )
            for sentence in sentence_dbs:
                Sentence.objects.create(
                    document=doc,
                    user=doc.user,
                    ordering=sentence.ordering,
                    language_code=doc.language_code,
                    text=sentence.text,
                )
        elif document.sentences and document.sentences != doc.sentences:
            # Delete the extras
            if existing_doc:
                for existing_sentence in existing_doc.sentence_set:
                    try:
                        sentence = list(filter(
                            lambda x: x.id == existing_sentence.id,
                            document.sentences,
                        ))[0]
                    except IndexError:
                        existing_sentence.delete()
                    else:
                        # We're only going to allow changes of the ordering,
                        # language, and text
                        existing_sentence.ordering = sentence.ordering
                        existing_sentence.language_code = doc.language_code
                        existing_sentence.text = sentence.text
                        existing_sentence.save()

            # Add the new sentences or raise an objection
            # if the sentence isn't new, but the document can't find it.
            for sentence in document.sentences:
                if not sentence.id:
                    Sentence.objects.create(
                        document=doc,
                        user=doc.user,
                        ordering=sentence.ordering,
                        language_code=doc.language_code,
                        text=sentence.text,
                    )
                elif existing_doc and not existing_doc.sentence_set.filter(
                    id=sentence_id,
                ):
                    # This is bad...where did this sentence come from,
                    # if it already has an ID,
                    # but the document doesn't know about it?
                    raise ObjectNotFoundError(
                        'Could not update sentence with id '
                        f'{{sentence.id}} because it does not '
                        'belong to document {{doc.id}}.'
                    )

        doc.refresh_from_db()
        docdb = self._django_to_pydantic(doc)
        return docdb

    def get(self, id: uuid.UUID, user_id: uuid.UUID) -> DocumentDB:
        """
        Get the specified document by id.
        Both the id and user id are supplied
        to make sure we don't return a document that the user doesn't own.

        :id: The id of the document
        :user_id: The user's id that owns the document

        :return: DocumentDB matching the id.
        :raises: ObjectNotFoundError if no matching document is found
            for the user
        """

        try:
            doc = Document.objects.prefetch_related('sentence_set') \
                    .select_related('user') \
                    .get(id=id, user__id=user_id)
        except Document.DoesNotExist as exc:
            raise ObjectNotFoundError(exc)

        docdb = self._django_to_pydantic(doc)
        return docdb

    def get_all(self, user_id: uuid.UUID) -> List[DocumentDB]:
        """
        Get all documents for the specified user.

        :user_id: The user's id who owns the documents

        :return: List of documents (may be empty)
        """
        docs = Document.objects.prefetch_related('sentence_set') \
                .select_related('user') \
                .filter(user__id=user_id).all()
        docdbs = [self._django_to_pydantic(doc) for doc in docs]
        return docdbs
