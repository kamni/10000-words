"""
Copyright (C) J Leadbetter <j@jleadbetter.com>
Affero GPL v3
"""

from pathlib import Path
from typing import Generator

import pytest
import pytest_asyncio
from nicegui.testing import User

from common.stores.app import AppStore
from common.utils.singleton import Singleton

from frontend.main import startup


pytest_plugins = ['nicegui.testing.plugin']


TEST_CONFIG_DIR = Path(__file__).resolve().parent.parent
TEST_CONFIG = TEST_CONFIG_DIR / 'setup.cfg'


@pytest_asyncio.fixture
async def user(user: User) -> Generator[User, None, None]:
    AppStore.destroy_all()
    startup(config=TEST_CONFIG, subsection='dev.in_memory')
    yield user
