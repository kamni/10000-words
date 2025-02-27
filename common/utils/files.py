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

    :return: Path to the 10,000 Words project directory
    """
    top_level_dir = Path(__file__).resolve().parent.parent.parent
    return top_level_dir


def get_upload_dir():
    """
    Get the absolute path to the upload directory.

    :return: Path as to the upload directory.
    """
    config = ConfigStore()
    base_path = config.get('common', 'UploadDir')

    # It's already an absolute directory
    if base_path.startswith('/'):
        return Path(base_path)

    top_level_dir = Path(__file__).resolve().parent.parent.parent
    full_path = top_level_dir / base_path
    return full_path
