"""
Copyright (C) J Leadbetter <j@jleadbetter.com>
Affero GPL v3
"""

import uuid
from enum import StrEnum
from typing import List, Optional

from pydantic import BaseModel

from ..utils.languages import LanguageCode
from .base import HashableMixin


class SentenceDB(HashableMixin, BaseModel):
    """
    Database representation of a sentence.
    """
    id: Optional[uuid.UUID] = None  # The database/adapter sets this value
    user_id: uuid.UUID

    # Example sentences might not have a document or ordering,
    # which is why document_id and ordering are optional.
    document_id: Optional[uuid.UUID] = None
    ordering: Optional[int] = None  # Relative to the document

    language_code: LanguageCode
    text: str
    enabled_for_study: Optional[bool] = False

    # These will be added after creation,
    # so these are also optional.
    display_text: Optional[List['DisplayTextDB']] = []
    translations: Optional[List['SentenceDB']] = []

    class Config:
        exclude_defaults = True
        use_enum_values = True

    @property
    def unique_fields(self):
        return ['user_id', 'text', 'language_code']


class SentenceUI(HashableMixin, BaseModel):
    """
    UI representation of a sentence.
    """
    id: uuid.UUID
    language: str
    ordering: Optional[int] = None
    text: str
    enabledForStudy: bool
    # A sentence can't be displayed in the UI without its display text,
    # so this is mandatory, unlike when creating the SentenceDB
    displayText: List['DisplayTextUI']
    translations: Optional[List['SentenceUI']] = []


class DisplayTextDB(HashableMixin, BaseModel):
    """
    Preserves the original version/case of the word for the sentence/document.
    Allows us to store the same word for multiple variations.
    Also tracks word order in the sentence.
    """

    id: Optional[uuid.UUID] = None  # Should be set by database/adapter
    user_id: uuid.UUID
    sentence_id: uuid.UUID
    word_id: uuid.UUID
    ordering: int  # Relative to the sentence
    language_code: LanguageCode
    text: str

    @property
    def unique_fields(self):
        return ['user_id', 'sentence_id', 'word_id', 'ordering']


class DisplayTextUI(HashableMixin, BaseModel):
    """
    Representation of display text for individual words in the UI.
    """
    id: uuid.UUID
    sentenceId: uuid.UUID
    word: 'WordUI'
    ordering: int
    language: str
    text: str


class WordStatus(StrEnum):
    """
    Statuses for a certain word or word phrase.

    How the statuses work:

    1. Not Set: User has not yet set a status on this word
    2. Ignored: this word doesn't have much value in learning
       -- e.g. articles like "the", conjunctions like "and",
       and prepositions that don't translate well.

    3. Learned: words that the user feels fluently comfortable with.

    4. To Learn: adds the words to a queue to introduce in future lessons.

    5. Learning: currently in circulation for learning exercises.
    """
    not_set = 'not_set'
    ignored = 'ignored'
    learned = 'learned'
    to_learn = 'to_learn'
    learning = 'learning'


class WordDB(HashableMixin, BaseModel):
    """
    Representation of a word in the database.

    A word represents a unit of grammar or meaning
    that can be learned and shared across multiple display texts.
    Does not have to be a single word.
    For example, 'good morning' and 'Good morning!' might be display texts
    that share the same Word.
    """

    id: Optional[uuid.UUID] = None  # Set by database/adapter
    user_id: uuid.UUID
    sentence_ids: Optional[List[uuid.UUID]] = []
    display_text_ids: Optional[List[uuid.UUID]] = []
    status: Optional[WordStatus] = 'not_set'
    language_code: LanguageCode
    text: str  # Case-insensitive, unlike DisplayText; always lower-case.

    class Config:
        exclude_defaults = True
        use_enum_values = True

    @property
    def unique_fields(self):
        return ['user_id', 'language_code', 'text']


class WordUI(HashableMixin, BaseModel):
    """
    Representation of a word in the UI
    """

    id: uuid.UUID
    sentences: List[SentenceUI]
    status: WordStatus
    language: str
    text: str

    class Config:
        exclude_defaults = True
        use_enum_values = True
