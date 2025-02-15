#!/usr/bin/env python

"""
Copyright (C) J Leadbetter <j@jleadbetter.com>
Affero GPL v3

Generate some manual test data and store it as JSON.

NOTE: You do not need to run this, unless the models change.
The output is stored in tests/data/db.json.
"""

import argparse
import json
import os
import random
import sys
import uuid
from pathlib import Path
from typing import List

PROJECT_DIR = Path(__file__).resolve().parent.parent.as_posix()
if PROJECT_DIR not in sys.path:
    sys.path.append(PROJECT_DIR)

from common.models.documents import DocumentDB
from common.models.settings import AppSettingsDB
from common.models.users import UserDB
from common.stores.data.in_memory import Database


DATA_DIR = os.path.join('scripts', 'data')
DB_FILE = 'db.json'


def create_settings() -> AppSettingsDB:
    """
    Generate app settings with the following configuration:

    - `multiuser_mode = True`
    - `passwordless_login = False`
    - `show_users_on_login_screen = True`

    These settings allow testing the full range of features of the app.
    """
    app_settings = AppSettingsDB(
        multiuser_mode=True,
        passwordless_login=False,
        show_users_on_login_screen=True,
    )
    return app_settings


def create_users() -> List[UserDB]:
    """
    Creates test users for the app.

    The first user is always an admin, username 'dev-admin'.
    The password for all users is 'dev'.
    """
    users: List[UserDB] = []
    admin = UserDB(
        id=uuid.uuid4(),
        username='dev-admin',
        display_name='Dev Admin',
        password='dev',
        is_admin=True,
    )
    users.append(admin)
    users.extend([
        UserDB(
            id=uuid.uuid4(),
            username=f'user0{idx}',
            display_name=f'User 0{idx}',
            password='dev',
        ) for idx in range(2)
    ])
    return users


def create_documents(users: List[UserDB]) -> List[DocumentDB]:
    """
    Create some test documents for the app.

    Users get a random selection of documents from the test data.

    :return: List of created documents
    """
    docs: List[DocumentDB] = []
    test_dir_full = os.path.join(PROJECT_DIR, DATA_DIR)
    languages = ('de', 'en', 'nl')

    for user in users:
        for lang in languages:
            lang_dir = os.path.join(test_dir_full, lang)
            num_docs = random.randint(1, 3)
            rand_docs: List[str] = []

            while len(rand_docs) < num_docs:
                doc_choice = random.choice(os.listdir(lang_dir))
                if doc_choice not in rand_docs:
                    rand_docs.append(doc_choice)

            for doc_name in rand_docs:
                file_path = os.path.join(DATA_DIR, lang, doc_name)
                docdb = DocumentDB(
                    id=uuid.uuid4(),
                    user_id=user.id,
                    display_name=doc_name.split('.')[0].replace('-', ' ').title(),
                    language_code=lang,
                    file_path=file_path,
                )
                docs.append(docdb)

    return docs


def create_database() -> Database:
    """
    Generate a Database object with test data
    """
    database = Database(
        users=[],
        documents=[],
    )
    app_settings = create_settings()
    database.app_settings = app_settings

    users = create_users()
    database.users = users

    documents = create_documents(users)
    database.documents = documents
    return database


if __name__ == '__main__':
    database = create_database()
    json_str = database.model_dump_json()
    parsed = json.loads(json_str)
    formatted = json.dumps(parsed, indent=4)

    db_file = os.path.join(PROJECT_DIR, DATA_DIR, DB_FILE)
    with open(os.path.join(PROJECT_DIR, DATA_DIR, DB_FILE), 'w') as db:
        db.write(formatted)
