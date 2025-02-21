"""
Copyright (C) J Leadbetter <j@jleadbetter.com>
Affero GPL v3
"""

import logging
import re
import string
import sys
import uuid
from pathlib import Path
from typing import Dict, List, Optional

from nicegui import app
from nicegui.observables import ObservableDict

PROJECT_DIR = Path(__file__).resolve().parent.parent.parent
if PROJECT_DIR.as_posix() not in sys.path:
    sys.path.append(PROJECT_DIR.as_posix())

from common.utils.singleton import Singleton
from prototypes.edit01.models import (
    DisplayText,
    Document,
    MockDatabase,
    Sentence,
    User,
    Word,
    WordStatus,
)


DATA_DIR = PROJECT_DIR / 'scripts' / 'data' / 'en'


class EditViewController(metaclass=Singleton):
    """
    Handle data manipulation for the EditView
    """

    DATA = [
        ('Little-Red-Riding-Hood.txt', 'Little Red Riding Hood', 'English'),
        #('Rumpelstiltskin.txt', 'Rumpelstiltskin', 'English'),
        #('The-Bremen-town-musicians.txt', 'The Bremen Town Musicians', 'English'),
    ]

    def __init__(self):
        # TODO: give everything a logger, including widgets and views
        self.logger = logging.getLogger(__name__)
        self._datastore: List[MockDatabase] = []

    @property
    def datastore(self):
        if not self._datastore:
            for file, title, language in self.DATA:
                parser = DocumentParser(
                    (DATA_DIR / file).as_posix(),
                    title,
                    language,
                )
                database = parser.parse()
                self._datastore.append(database)
        return self._datastore

    def get_documents(self):
        doc_dict = {
            'current_document': None,
            'all_documents': [],
        }
        for db in self.datastore:
            doc_dict['all_documents'].append(db.document.model_dump())

        return doc_dict

    def get_sentences(self):
        sentence_dict = {}
        for db in self.datastore:
            sentences = {
                str(id): sentence_obj.model_dump()
                for id, sentence_obj in db.sentences.items()
            }
            sentence_dict.update(sentences)

        return sentence_dict

    def get_words(self):
        word_dict = {}
        for db in self.datastore:
            words = {
                str(id): word_obj.model_dump()
                for id, word_obj in db.words.items()
            }
            word_dict.update(words)

        return word_dict


class EditComponentController(metaclass=Singleton):
    """
    Handle data manipulation for the EditComponents
    """

    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def create_document(self, **kwargs) -> Document:
        # TODO: write to database
        parser = DocumentParser(
            document_path='',
            display_name=kwargs.get('displayName'),
            language=kwargs.get('language'),
        )
        data = kwargs.get('binaryData').data.decode('utf-8')
        sentence_text = data.split('\n')
        mockdb = parser.parse(sentence_text)
        return mockdb.model_dump()

    def get_current_document(self, doc: Dict) -> Document:
        if doc:
            return Document(**doc)
        return None

    def get_current_document_dict(self, doc: Document) -> Dict:
        return doc.model_dump()

    def get_documents(self, docs: List[Dict]) -> List[Document]:
        return [Document(**doc) for doc in docs]

    def set_word_status(
        self,
        id: uuid.UUID,
        status: WordStatus,
        client_storage: ObservableDict,
    ):
        # TODO: needs to write back to database
        # TODO: should update document and sentences
        word_dict = client_storage['words'].get(str(id))
        if word_dict:
            word_dict['status'] = status


class DocumentParser:
    def __init__(self, document_path: str, display_name=str, language=str):
        self.document_path = document_path
        self.document_display_name = display_name
        self.language = language
        self.database = MockDatabase()

    def make_document_obj(self, user=User) -> Document:
        doc = Document(
            id=uuid.uuid4(),
            user=user,
            displayName=self.document_display_name,
            language=self.language,
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

    def parse(self, sentence_texts: Optional[List[str]]=None) -> MockDatabase:
        user = User(
            id=uuid.uuid4(),
            displayName='Dev Admin',
            username='dev-admin',
            isAdmin=True,
        )

        document = self.make_document_obj(user)
        self.database.document = document

        sentence_texts = sentence_texts or self.read_document()
        sentences = [
            self.make_sentence_obj(text, idx + 1)
            for idx, text in enumerate(sentence_texts)
        ]

        for sentence in sentences:
            self.database.sentences[str(sentence.id)] = sentence
            raw_texts = tokenize_sentence(sentence)
            words = [
                self.make_word_obj(text, sentence)
                for text in raw_texts
            ]
            for idx, (word, raw_text) in enumerate(zip(words, raw_texts)):
                if word.id not in self.database.words:
                    self.database.words[str(word.id)] = word
                display_text = self.make_display_text_obj(
                    raw_text, sentence, idx + 1, word,
                )
                sentence.word_display_text.append(display_text)

        document.sentences = sentences
        return self.database


# This is potentially a util that can be used in more than one place
def tokenize_sentence(sentence: Sentence) -> List[str]:
    tokens = []

    def add_punctuation_to_tokens(punctuation: str):
        if punctuation:
            if len(punctuation) > 1:
                tokens.extend(list(punctuation))
            else:
                tokens.append(punctuation)

    sentence_bits = sentence.text.split(' ')
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
    parser = DocumentParser(document_path, 'Rumpelstiltskin', 'English')
    database = parser.parse()
    print_document(database)
