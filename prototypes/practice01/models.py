"""
Copyright (C) J Leadbetter <j@jleadbetter.com>
Affero GPL v3
"""

from enum import StrEnum
from typing import Any, List, Optional

from pydantic import BaseModel

from common.utils.languages import LanguageCode


class Document(BaseModel):
    display_name: Optional[str] = None
    author: Optional[str] = None
    language_code: Optional[LanguageCode] = None
    sentences: Optional[List['Sentence']] = []

    class Config:
        use_enum_values = True


class Sentence(BaseModel):
    text: str
    language_code: Optional[LanguageCode] = None
    ordering: Optional[int]
    enabled_for_study: Optional[bool] = False
    display_text: Optional[List['DisplayText']] = []
    translations: Optional[List['Sentence']] = []

    class Config:
        use_enum_values = True


class DisplayText(BaseModel):
    sentence_ordering: int
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
    sentence_ordering: int
    display_text_ordering: int
    text: str
    language_code: Optional[LanguageCode] = None
    status: Optional[WordStatus] = 'not_set'
    examples: Optional[List[Sentence]] = []

    class Config:
        use_enum_values = True
