"""
Copyright (C) J Leadbetter <j@jleadbetter.com>
Affero GPL v3
"""

import pytest
from nicegui import ui
from nicegui.testing import User


@pytest.mark.asyncio
async def test_redirects_when_not_logged_in(user: User):
    pass


@pytest.mark.asyncio
async def test_first_time_logged_in_no_documents(user: User):
    # Test left, center, and middle columns
    # Test upload document first time
    pass


@pytest.mark.asyncio
async def test_existing_documents(user: User):
    # Test left, center, and middle columns
    # Test select document
    # Test upload
    pass

# TODO: tests for validation, after validation added
