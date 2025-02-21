"""
Copyright (C) J Leadbetter <j@jleadbetter.com>
Affero GPL v3
"""

import uuid
from enum import StrEnum
from typing import Dict, List, Optional

from pydantic import BaseModel


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
    not_set = 'Not Set'
    ignored = 'Ignored'
    learned = 'Learned'
    to_learn = 'To Learn'
    learning = 'Learning'


class User(BaseModel):
    id: uuid.UUID
    displayName: str
    username: str
    isAdmin: bool


class Document(BaseModel):
    id: uuid.UUID
    user: User
    displayName: str
    language: Optional[str] = 'English'
    sentences: Optional[List['Sentence']] = []


class Sentence(BaseModel):
    id: uuid.UUID
    # Don't forget user_id in real version
    document_id: uuid.UUID
    ordering: int
    text: str
    # We'll add these later...
    # translations: Optional[List[Sentence]] = []
    word_display_text: Optional[List['DisplayText']] = []


class Word(BaseModel):
    """
    A 'Word' object represents a meaningful unit in the language.
    It does not have to be only a singular word.
    For example, it could be a phrase ('thank you')
    or a verb that is always matched with a preposition ('pick up').
    """
    id: uuid.UUID
    # Don't forget user_id in real version
    case_insensitive_text: str  # unique; used to check for duplicates
    status: Optional[WordStatus] = WordStatus.not_set
    # This will be used in the 'Practice' part of the app
    sentences: Optional[List[uuid.UUID]] = []


class DisplayText(BaseModel):
    """
    Preserves the original version/case of the word for the sentence/document.
    Allows us to store the same word for multiple variations.
    Also tracks word order in the sentence.
    """
    # Don't forget user_id in real version
    text: str
    sentence_id: uuid.UUID  # One-to-many back-link with Sentence
    word: Word  # One-to-many back-link with Word
    ordering: int


class MockDatabase(BaseModel):
    """
    Only models one document for this prototype.
    We're ignoring DisplayText here,
    because we'll usually only access it through the Sentences.
    """
    document: Optional[Document] = None
    sentences: Optional[Dict[str, Sentence]] = {}
    words: Optional[Dict[str, Word]] = {}
