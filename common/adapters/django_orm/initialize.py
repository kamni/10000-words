"""
Copyright (C) J Leadbetter <j@jleadbetter.com>
Affero GPL v3

Utilities for stores
"""

import os
import sys
from pathlib import Path


def init_django():
    """
    Make sure the Django ORM can work even when the Django server isn't running
    """

    import django
    from django.conf import settings

    if not os.environ.get('DJANGO_SETTINGS_MODULE'):
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.core.settings')
    os.environ.setdefault('DJANGO_ALLOW_ASYNC_UNSAFE', 'true')

    backend_dir = Path(__file__).resolve().parent.parent.parent.parent / 'backend'
    if backend_dir.as_posix() not in sys.path:
        sys.path.append(backend_dir.as_posix())

    if settings.configured:
        return

    django.setup()
