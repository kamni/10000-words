"""
Copyright (C) J Leadbetter <j@jleadbetter.com>
Affero GPL v3
"""

import os
from pathlib import Path
from typing import Union

from common.models.documents import DocumentDB
from common.stores.config import ConfigStore


def get_project_dir():
    """
    Get the absolute path to this project's directory.

    :return: Path as string to the 10,000 Words project directory
    """
    top_level_dir = Path(__file__).resolve().parent.parent.parent
    return top_level_dir.as_posix()


def get_upload_dir():
    """
    Get the absolute path to the upload directory.

    :return: Path as string to the upload directory.
    """
    config = ConfigStore()
    base_path = config.get('common', 'UploadDir')

    # It's already an absolute directory
    if base_path.startswith('/'):
        return base_path

    top_level_dir = Path(__file__).resolve().parent.parent.parent
    full_path = top_level_dir / base_path
    return full_path.as_posix()


def document_upload_path(
    instance: Union[DocumentDB, 'Document'],
    filename: str,
) -> str:
    """
    Get the relative upload path for a document.

    :instance: An implementation of DocumentBase
    :filename: Name of file being uploaded

    :return: Path as string to the uploaded document.
        Path will be relative to `UploadDir` in setup.cfg
    """

    try:
        user_id = instance.user_id
    except AttributeError:
        user_id = instance.user.id

    path = os.path.join(
        str(user_id),
        instance.language_code,
        'docs',
        filename,
    )
    return path
