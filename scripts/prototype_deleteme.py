#!/usr/bin/env python

"""
Copyright (C) J Leadbetter <j@jleadbetter.com>
Affero GPL v3
"""

import re
import uuid
import string
import sys
from enum import StrEnum
from pathlib import Path
from typing import Dict, List, Optional

from pydantic import BaseModel

PROJECT_DIR = Path(__file__).resolve().parent.parent
if PROJECT_DIR.as_posix() not in sys.path:
    sys.path.append(PROJECT_DIR.as_posix())


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
    display_text: str
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
    sentences: Optional[List[Sentence]] = []
    words: Optional[Dict[str, Word]] = {}


class DocumentParser:
    def __init__(self, document_path: str, display_name=str):
        self.document_path = document_path
        self.document_display_name = display_name
        self.database = MockDatabase()

    def make_document_obj(self, user=User) -> Document:
        doc = Document(
            id=uuid.uuid4(),
            user=user,
            displayName=self.document_display_name,
        )
        return doc

    def read_document(self) -> List[str]:
        # For the first version of the app,
        # we expect one sentence per line.
        with open(self.document_path, 'r') as doc:
            sentence_texts = doc.readlines()
        return sentence_texts

    def make_sentence_obj(self, sentence_text: str, ordering: int) -> Sentence:
        document = self.database.document
        sentence = Sentence(
            id=uuid.uuid4(),
            document_id=document.id,
            ordering=ordering,
            display_text=sentence_text.strip(),
        )
        return sentence

    def tokenize_sentence(self, sentence: Sentence) -> List[str]:
        tokens = []

        def add_punctuation_to_tokens(punctuation: str):
            if punctuation:
                if len(punctuation) > 1:
                    tokens.extend(list(punctuation))
                else:
                    tokens.append(punctuation)

        sentence_bits = sentence.display_text.split(' ')
        for item in sentence_bits:
            item = item.strip()
            if not item:
                # The documents are currently one sentence per line.
                # We want to keep the empty lines as paragraph breaks.
                tokens.append(item)
                continue
            if item.isdecimal() or item.isdigit():
                tokens.append(item)
                tokens.append(' ')
                continue

            only_punctuation = re.compile(r"^[^\w]+$")
            before = re.compile(r"^([^\w]*)(.*)$")
            after = re.compile(r"([\w\-_]+('\w+)*)([^\w]*)$")

            if only_punctuation.match(item):
                add_punctuation_to_tokens(item)
                tokens.append(' ')
                continue

            punctuation, rest_of_bit = before.match(item).groups()
            add_punctuation_to_tokens(punctuation)

            word, _ignored, punctuation = after.match(rest_of_bit).groups()
            tokens.append(word)
            add_punctuation_to_tokens(punctuation)

            # And we want to add the space back that we had
            # when we originally split the sentence
            tokens.append(' ')

        return tokens

    def make_word_obj(self, text: str, sentence: Sentence) -> Word:
        case_insensitive_text = text.strip().lower()
        existing_word = list(
            filter(
                lambda x: x[1].case_insensitive_text == case_insensitive_text,
                self.database.words.items(),
            )
        )
        if existing_word:
            word = existing_word[0][1]
            word.sentences.append(sentence.id)
            return word

        if (
            not case_insensitive_text
            or case_insensitive_text in (string.punctuation)
            or case_insensitive_text.isdigit()
        ):
            word_status = WordStatus.ignored
            if not case_insensitive_text:
                # We don't want to mess with intentional whitespace characters
                case_insenstive_text = text
        else:
            word_status = WordStatus.not_set

        word = Word(
            id=uuid.uuid4(),
            case_insensitive_text=case_insensitive_text,
            sentences=[sentence.id],
            status = word_status,
        )
        return word

    def make_display_text_obj(
        self,
        text: str,
        sentence: Sentence,
        ordering: int,
        word: Word,
    ) -> DisplayText:
        display_text = DisplayText(
            text=text,
            sentence_id=sentence.id,
            ordering=ordering,
            word=word,
        )
        return display_text

    def parse(self) -> MockDatabase:
        user = User(
            id=uuid.uuid4(),
            displayName='Dev Admin',
            username='dev-admin',
            isAdmin=True,
        )

        document = self.make_document_obj(user)
        self.database.document = document

        sentence_texts = self.read_document()
        sentences = [
            self.make_sentence_obj(text, idx + 1)
            for idx, text in enumerate(sentence_texts)
        ]
        self.database.sentences = sentences

        for sentence in sentences:
            raw_texts = self.tokenize_sentence(sentence)
            words = [
                self.make_word_obj(text, sentence)
                for text in raw_texts
            ]
            for idx, (word, raw_text) in enumerate(zip(words, raw_texts)):
                if word.id not in self.database.words:
                    self.database.words[word.id] = word
                display_text = self.make_display_text_obj(
                    raw_text, sentence, idx + 1, word,
                )
                sentence.word_display_text.append(display_text)

        document.sentences = sentences
        return self.database


def print_document(database: MockDatabase):
    print(database.document.displayName)
    print('-------')
    for sentence in database.document.sentences:
        item = ''.join([
            display_text.text
            for display_text in sentence.word_display_text
        ])
        print(item)


if __name__ == '__main__':
    document_path = PROJECT_DIR / 'scripts' / 'data' / 'en' / 'Rumpelstiltskin.txt'
    parser = DocumentParser(document_path, 'Rumpelstiltskin')
    database = parser.parse()
    print_document(database)
