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
        for sentence in document.sentences:
            sentence.id = uuid.uuid4()
    id: Optional[uuid.UUID] = None
    translation_id: Optional[uuid.UUID] = None
    text: str
    language_code: Optional[LanguageCode] = None
    ordering: Optional[int]
    enabled_for_study: Optional[bool] = False
    display_text: Optional[List['DisplayText']] = []
    translations: Optional[List['Sentence']] = []
        pass

    def _load_db_db(self, db: MockDatabase) -> MockDatabase:
        pass
