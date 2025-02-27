"""
Copyright (C) J Leadbetter <j@jleadbetter.com>
Affero GPL v3
"""

import os
import random
import string
import uuid
from typing import Optional

from common.utils.languages import LanguageCode, language_choices


def random_email(username: Optional[str]=None, domain: Optional[str]=None) -> str:
    username = username or random_string()
    if not domain:
        company = random_string()
        extension = random.choice(['com', 'net', 'org', 'ninja'])
        domain = f'{company}.{extension}'
    email = f'{username}@{domain}'
    return email


def random_file_path(
    base_path: Optional[str]=None,
    extension: Optional[str]=None,
) -> str:
    if not base_path:
        num_parts = random.randrange(3, 5)
        base_path = os.path.join(*[
            random_string() for i in range(num_parts)
        ])
    if not extension:
        extension = random.choice(['json', 'mp3', 'txt'])
    filename = random_string()

    file_path = os.path.join(base_path, f'{filename}.{extension}')
    return file_path


def random_language_code():
    lang_code = str(random.choice(list(LanguageCode)))
    return lang_code


def random_language():
    lang = random.choice(list(language_choices.keys()))
    return lang


def random_password(min_size: int=10, max_size: int=20) -> str:
    data_str = ''.join([
        random.choice(string.ascii_lowercase + string.digits)
        for i in range(random.randrange(min_size, max_size))
    ])
    return data_str


def random_string(min_size: int=8, max_size: int=12) -> str:
    data_str = ''.join([
        random.choice(string.ascii_lowercase)
        for i in range(random.randrange(min_size, max_size))
    ])
    return data_str


def random_uuid():
    return str(uuid.uuid4())
