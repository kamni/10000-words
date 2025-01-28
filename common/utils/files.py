"""
Copyright (C) J Leadbetter <j@jleadbetter.com>
Affero GPL v3
"""

import os
from typing import Any

from ..models.documents import DocumentBase


def document_upload_path(instance: DocumentBase, filename: str) -> str:
    """
    Get the upload path for a document.

    :instance: An implementation of DocumentBase
    :filename: Name of file being uploaded

    :return: Path as string to the uploaded document.
        Path will be relative to `UploadDir` in setup.cfg
    """

    path = os.path.join(
        str(instance.user.id),
        instance.language_code,
        'docs',
        filename,
    )
    return path
