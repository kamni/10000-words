"""
Copyright (C) J Leadbetter <j@jleadbetter.com>
Affero GPL v3
"""

from pydantic import BaseModel


class BinaryFileData(BaseModel):
    """
    Represents binary data that should be written to a file.
    Used when uploading documents.
    """
    name: str
    data: bytes
