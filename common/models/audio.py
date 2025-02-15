"""
Copyright (C) J Leadbetter <j@jleadbetter.com>
Affero GPL v3
"""

from typing import Optional

from pydantic import BaseModel

from .base import HashableMixin
from ..utils.languages import LanguageCode


class AudioFileUI(HashableMixin, BaseModel):
    """
    Representation of an audio file in the UI.
    """

    languageCode: LanguageCode
    text: str
    file_path: str

    @property
    def unique_fields(self):
        return ['file_path']
