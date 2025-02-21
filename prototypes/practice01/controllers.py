"""
Copyright (C) J Leadbetter <j@jleadbetter.com>
Affero GPL v3
"""

import uuid
from pathlib import Path
from typing import Any, Dict, Optional

import toml

from prototypes.practice01.models import Document, MockDatabase


class DatabaseController:
    """
    Manages the state of the app for the entire database.

    NOTE: This is only a single controller for the prototype.
    Break this into adapters and specific controllers later.
    """

    def __init__(self, input_file: Path, output_file: Optional[Path]=None):
        self.input_file = input_file
        self.output_file = output_file or input_file
        self.db = MockDatabase()
        self.load_data()

    def load_data(self):
        with self.input_file.open('r') as infile:
            data = toml.load(infile)

        # If this is the first time loading the database
        # from the output of scripts.py,
        # we want to save it to the new output file.
        do_save = False

        # We're loading a db generated from scripts.py
        if 'document' in data:
            temp_db = MockDatabase(
                documents=Document.model_validate(data['document']),
            )
            db = self._load_scripts_data(temp_db)
            do_save = True
        # We've loaded this before; just set up the model relations
        else:
            temp_db = MockDatabase.model_validate(data)
            db = self._load_db_data(temp_db)

        self.db = db
        if do_save:
            self.save_data()

    # TODO: don't forget to manually call save_data when changes are made

    def save_data(self):
        data = self.db.model_dump(exlude_defaults=True)
        with self.output_file.open('w') as outfile:
            toml.dump(data, outfile)

    def _load_scripts_db(self, db: MockDatabase) -> MockDatabase:
        document = db.documents[0]
        document.id = uuid.uuid4()

        for sentence in document.sentences:
            sentence.id = uuid.uuid4()
            db.sentences[sentence.id] = sentence

            tokens = tokenize_sentence(sentence)
            words = [self._get_word(token) for token in tokens]
            for idx, (word, token) in enumerate(zip(words, tokens)):
                existing_word = self._get_existing_word
                if not existing_word:
                    db.words[word.id] = word

                display_text = _make_display_text(token, idx+1)
                db.display_text[display_text.id] = display_text

                # Linking and backlinking
                display_text.sentence_id = sentence.id
                display_text.word = word
                word.display_text_ids.append(display_text.id)
                word.sentence_ids.append(sentence.id)
                sentence.display_text.append(display_text)

        return db

    def _load_db_data(self, db: MockDatabase) -> MockDatabase:
        pass

    def _make_word(self, token: str):
        pass

    def _make_display_text(self, text: str):
        pass

    def _get_existing_word(self, text: str):
        pass


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
