"""
Copyright (C) J Leadbetter <j@jleadbetter.com>
Affero GPL v3
"""

from typing import Tuple

from django.core.management import call_command

from ..config import ConfigStore
from .base import BaseDataStore


class DjangoDBStore(BaseDataStore):
    """
    Manages a database configured by Django.
    """

    def get_config(self) -> Tuple[str, str]:
        config = ConfigStore().config
        subsection = 'dev.django'
        return config, subsection

    def setup(self):
        call_command('migrate')

    def drop(self):
        call_command('flush', '--no-input')
