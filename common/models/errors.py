"""
Copyright (C) J Leadbetter <j@jleadbetter.com>
Affero GPL v3
"""

from typing import List


class ObjectExistsError(Exception):
    """
    Thrown when trying to add an object that already exists.
    """
    pass


class ObjectNotFoundError(Exception):
    """
    Thrown when trying to retrieve an object that doesn't exist.
    """
    pass


class ObjectValidationError(Exception):
    """
    Thrown when validation of an object fails.
    """

    def __init__(self, messages: List[str]):
        self.messages = messages
