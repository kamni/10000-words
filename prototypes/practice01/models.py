"""
Copyright (C) J Leadbetter <j@jleadbetter.com>
Affero GPL v3
"""

import uuid
from enum import StrEnum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field

from common.utils.languages import LanguageCode


class Document(BaseModel):
    display_name: Optional[str] = None
    author: Optional[str] = None
    language_code: Optional[LanguageCode] = None
    sentences: Optional[List['Sentence']] = []
    words: Optional[List['Word']] = []

    class Config:
        exclude_default = True
        use_enum_values = True


class Sentence(BaseModel):
    id: uuid.UUID = Field(default_factory=uuid.uuid4)
    text: str
    language_code: LanguageCode
    ordering: Optional[int] = None
    enabled_for_study: Optional[bool] = False
    translations: Optional[List['Sentence']] = []
    translation: Optional['Sentence'] = None

    class Config:
        exclude_default = True
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
    id: uuid.UUID = Field(default_factory=uuid.uuid4)
    text: str
    language_code: LanguageCode
    status: Optional[WordStatus] = 'not_set'
    example_sentence_ids: Optional[List[uuid.UUID]] = []
    translation: Optional['Word'] = None

    class Config:
        exclude_default = True
        use_enum_values = True

    def __hash__(self):
        return hash(self.text)
