"""
Copyright (C) J Leadbetter <j@jleadbetter.com>
Affero GPL v3
"""

import uuid
from enum import StrEnum
from typing import Any, List, Optional

from pydantic import BaseModel

from common.utils.languages import LanguageCode


class Document(BaseModel):
    id: Optional[uuid.UUID] = None
    display_name: Optional[str] = None
    author: Optional[str] = None
    language_code: Optional[LanguageCode] = None
    sentences: Optional[List['Sentence']] = []

    class Config:
        use_enum_values = True


class Sentence(BaseModel):
    id: Optional[uuid.UUID] = None
    document_id: Optional[uuid.UUID] = None
    translation_id: Optional[uuid.UUID] = None
    text: str
    language_code: Optional[LanguageCode] = None
    ordering: Optional[int]
    enabled_for_study: Optional[bool] = False
    display_text: Optional[List['DisplayText']] = []
    translations: Optional[List['Sentence']] = []

    class Config:
        use_enum_values = True
        exclude = {'display_text', 'translations'}


class DisplayText(BaseModel):
    id: Optional[uuid.UUID] = None
    sentence_id: Optional[uuid.UUID] = None
    ordering: int
    text: str
    language_code: Optional[LanguageCode] = None
    word: 'Word'

    class Config:
        use_enum_values = True


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


class Word(BaseModel):
    id: Optional[uuid.UUID] = None
    display_text_ids: Optional[List[uuid.UUID]] = None
    sentence_ids: Optional[List[uuid.UUID]] = []
    text: str
    language_code: Optional[LanguageCode] = None
    status: Optional[WordStatus] = 'not_set'
    examples: Optional[List[Sentence]] = []

    class Config:
        use_enum_values = True


class MockDatabase(BaseModel):
    documents: Optional[Dict[uuid.UUID, Document]] = {}
    sentences: Optional[Dict[uuid.UUID, Sentence]] = {}
    display_text: Optional[Dict[uuid.UUID, DisplayText]] = {}
    words: Optional[Dict[uuid.UUID, Word]] = {}
