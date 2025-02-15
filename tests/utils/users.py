"""
Copyright (C) J Leadbetter <j@jleadbetter.com>
Affero GPL v3
"""

import random
import string

from common.models.users import UserDB, UserUI
from common.stores.adapter import AdapterStore

from .random_data import (
    random_email,
    random_password,
    random_string,
    random_uuid,
)


def make_user_db(**kwargs) -> UserDB:
    """
    Make a UserDB object, but don't write it to the database.

    :kwargs: arguments that will be passed to UserDB during creation.
    """

    username = random_string()
    random_data = {
        'username': username,
        'password': random_password(),
        'email': random_email(username=username),
        'display_name': username.title(),
    }
    random_data.update(kwargs)

    user = UserDB(**random_data)
    return user


def create_user_db(**kwargs) -> UserDB:
    """
    Make a UserDB object and save it to the database.

    :kwargs: arguments passed to the UserDB init
    """

    adapter = AdapterStore().get('UserDBPort')
    userdb = make_user_db(**kwargs)

    new_userdb = adapter.create(userdb)
    # We need the password for testing
    new_userdb.password = userdb.password
    return new_userdb


def make_user_ui(**kwargs) -> UserUI:
    """
    Create a UserUI object.
    Does not have a corresponding UserDB object.

    :kwargs: arguments that will be passed to UserUI during creation.
    """

    username = random_string()
    random_data = {
        'id': random_uuid(),
        'username': username,
        'displayName': username.title(),
    }
    random_data.update(kwargs)

    user = UserUI(**random_data)
    return user
