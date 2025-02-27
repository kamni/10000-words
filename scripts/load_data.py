#!/usr/bin/env python

"""
Copyright (C) J Leadbetter <j@jleadbetter.com>
Affero GPL v3
"""

import argparse
import os
import sys
from pathlib import Path

PROJECT_DIR = Path(__file__).resolve().parent.parent
if not PROJECT_DIR.as_posix() in sys.path:
    sys.path.append(PROJECT_DIR.as_posix())

from common.stores.app import AppStore

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.core.settings')

DEFAULT_CONFIG = (PROJECT_DIR / 'setup.cfg').as_posix()
DEFAULT_SUBSECTION = 'dev.django'


if __name__ == '__main__':
    # NOTE: Running this script with the InMemoryDBStore is pointless,
    # because the database will disappear once the script is complete.
    # For this reason, the only store that runs from the command line
    # is Django.
    # NOTE: WARNING: This forces a reload of the configuration.
    # Don't run this script while the server is running.
    parser = argparse.ArgumentParser(
        prog='LoadData',
        description=(
            'Load data from a TOML file into the database.\n'
            'Only works for the Django ORM. '
        ),

    )
    parser.add_argument(
        '-d',
        '--db-file',
        default=None,
        help=(
            'Path to the database file you want to load.\n'
            'If not specified, defaults to dev.django.adapters.dataport.DataFile '
            'in setup.cfg.'
        ),
    )
    args = parser.parse_args()

    print('---------------------------------------')
    print(
        'WARNING: This script will destroy the existing configuration on '
        'running servers, and will drop all tables in the database.'
    )
    print('---------------------------------------')

    doit = ''
    allowed_values = ('y', 'yes', 'n', 'no')
    while doit not in allowed_values:
        doit = input('Are you sure you want to continue? (y/n) ').lower()
        if doit not in allowed_values:
            print('Please choose either "y" or "n".')

    if doit in ('n', 'no'):
        print('Canceling...')
        sys.exit(0)

    AppStore.destroy_all()
    print('Initializing database...')
    apps = AppStore(DEFAULT_CONFIG, DEFAULT_SUBSECTION)
    store = apps.get('DataStore')
    print('Clearing database tables...')
    store.drop()
    print('Loading data into database...')
    store.load_data(db_file=args.db_file, force=True)
    print('Done!')
