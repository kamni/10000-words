"""
Copyright (C) J Leadbetter <j@jleadbetter.com>
Affero GPL v3
"""

from typing import Dict, List, Optional

from pydantic import BaseModel

from .documents import DocumentDB
from .settings import AppSettingsDB
from .sentences import DisplayTextDB, SentenceDB, WordDB
from .users import UserDB


class Database(BaseModel):
    """
    Representation of a database as a pydantic model.
    Used by the DataLoader and the InMemoryDatabase.
    """

    app_settings: Optional[AppSettingsDB] = None
    users: Optional[List[UserDB]] = []

    # Explanation of the setup:
    #
    # * documents: get all by user.id, for editing and practice
    # * words: get all by user.id and status for practice
    # * display_text: get for showing sentences in editing views
    # * sentences: get a list of sentences by word for practice
    documents: Optional[Dict[str, List[DocumentDB]]] = {}  # Key is user.id
    words: Optional[Dict[str, List[WordDB]]] = {}  # Key is (user.id, status)
    display_text: Optional[Dict[str, List[DisplayTextDB]]] = {}  # Key: sentence.id
    sentences: Optional[Dict[str, List[SentenceDB]]] = {}  # Key is word.id
