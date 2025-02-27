"""
Copyright (C) J Leadbetter <j@jleadbetter.com>
Affero GPL v3
"""

import pytest
from nicegui import ui
from nicegui.testing import User

from common.models.settings import AppSettingsDB
from common.stores.adapter import AdapterStore
from frontend import main
from tests.frontend.utils import login
from tests.utils.documents import create_document_db
from tests.utils.users import create_user_db


@pytest.mark.asyncio
@pytest.mark.module_under_test(main)
async def test_redirects_when_not_logged_in(user: User):
    settings = AdapterStore().get('AppSettingsDBPort')
    settings.create_or_update(AppSettingsDB())
    create_user_db()

    await user.open('/edit')
    await user.should_see('Login', kind=ui.label)


@pytest.mark.asyncio
@pytest.mark.module_under_test(main)
async def test_first_time_logged_in_no_documents(user: User):
    settings = AdapterStore().get('AppSettingsDBPort')
    settings.create_or_update(AppSettingsDB())
    userdb = create_user_db()
    await login(user, userdb)

    await user.open('/edit')
    await user.should_see('Welcome to 10,000 Words', kind=ui.label)
    await user.should_see('To get started', kind=ui.label)

    user.find('Upload', kind=ui.button).click()
    user.find('Cancel', kind=ui.button).click()

    user.find('Upload', kind=ui.button).click()
    user.find('Document Title', kind=ui.input).type('Roodkapje')
    # TODO: how do we interact with a select?
    #user.find('Language', kind=ui.select).type('German')
    # TODO: how do we upload a file?


@pytest.mark.asyncio
@pytest.mark.module_under_test(main)
async def test_existing_documents(user: User):
    settings = AdapterStore().get('AppSettingsDBPort')
    settings.create_or_update(AppSettingsDB())
    userdb = create_user_db()
    docdb = create_document_db(
        user_id=userdb.id,
        display_name='Foo',
        language_code='de',
    )
    await login(user, userdb)

    await user.open('/edit')
    await user.should_see('Choose an uploaded document', kind=ui.label)
    await user.should_see('German', kind=ui.expansion)
    user.find('Foo', kind=ui.button).click()
    await user.should_see('Foo', kind=ui.label)

# TODO: tests for validation, after validation added
