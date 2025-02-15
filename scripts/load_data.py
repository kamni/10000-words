#!/usr/bin/env python

"""
Copyright (C) J Leadbetter <j@jleadbetter.com>
Affero GPL v3
"""

import os
import sys
from pathlib import Path

PROJECT_DIR = Path(__file__).resolve().parent.parent
if not PROJECT_DIR.as_posix() in sys.path:
    sys.path.append(PROJECT_DIR.as_posix())

from common.stores.data.base import DataLoader

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.core.settings')

DEFAULT_CONFIG = (PROJECT_DIR / 'setup.cfg').as_posix()
DEFAULT_SUBSECTION = 'dev.django'


if __name__ == '__main__':
    # NOTE: Running this script with the InMemoryDBStore is pointless,
    # because the database will disappear once the script is complete.
    # For this reason, the only store that runs from the command line
    # is Django.
    loader = DataLoader(DEFAULT_CONFIG, DEFAULT_SUBSECTION, force_config=True)
    loader.load()
