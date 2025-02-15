"""
Copyright (C) J Leadbetter <j@jleadbetter.com>
Affero GPL v3
"""

import string
from collections.abc import Callable
from functools import partial
from typing import List, Optional

from nicegui import ui

from common.models.errors import ObjectExistsError, ObjectValidationError
from common.models.users import UserDB
from frontend.widgets.base import BaseWidget
from frontend.widgets.validate import (
    ValidatingInput,
    text_does_not_contain_spaces,
    text_equals_value,
    text_has_min_length,
    text_is_alphanumeric,
    text_is_lowercase,
)


class RegistrationWidget(BaseWidget):
    """
    Provides a registration form for a new user.
    """

    CSS = '''
        .q-input {
            width: 60% !important;
        }
    '''

    def display(self):
        self._display_name = ValidatingInput('Name (Optional)', 'display-name')
        self._username = ValidatingInput(
            'Username',
            'username',
            [
                partial(text_has_min_length, expected_length=4),
                text_does_not_contain_spaces,
                text_is_lowercase,
                text_is_alphanumeric,
            ],
        )
        self._password = None
        self._password_confirm = None
        if self.settings.show_password_field:
            self._password = ValidatingInput(
                'Password',
                'password',
                [
                    partial(text_has_min_length, expected_length=8),
                    text_does_not_contain_spaces,
                ],
                password=True,
                password_toggle_button=True,
            )
            self._password_confirm = ValidatingInput(
                'Confirm password',
                'confirm-password',
                show_title_in_errors=False,
                password=True,
                password_toggle_button=True,
            )

        def is_valid() -> bool:
            return all([
                self._display_name.validate(),
                self._username.validate(),
                self._password.validate() if self._password else True,
                self._password_confirm.validate() if self._password else True,
            ])

        adapter = self.adapters.get('UserDBPort')
        another_user_exists = adapter.get_first() is not None

        def save_user():
            if self._password:
                self._password_confirm.remove_validators()
                self._password_confirm.add_validator(
                    partial(
                        text_equals_value,
                        expected_value=self._password.value,
                    ),
                )
            if not is_valid():
                return

            user = UserDB(
                display_name=self._display_name.value,
                username=self._username.value,
                password=self._password.value if self._password else None,
            )
            # First user should always be an admin
            # so we have someone to manage the system
            if not another_user_exists:
                user.is_admin = True

            try:
                adapter.create(user)
            except ObjectExistsError:
                self._username.set_error(['already exists.'])
                return
            except ObjectValidationError as exc:
                # Currently the only validation in the backend is password
                self._password.set_error(exc.messages, include_title=False)
                return

            ui.notify(f'Success!')
            self.emit_done()

        ui.on('keydown.enter', save_user)

        with ui.card().classes('absolute-center'):
            ui.label('Register for 10,000 Words').classes('text-3xl')
            ui.separator()

            self._display_name.display()
            self._username.display()
            if self._password:
                self._password.display()
                self._password_confirm.display()

            ui.separator()
            with ui.row().classes('w-full'):
                if another_user_exists:
                    ui.button('Cancel', on_click=self.emit_cancel, color='warning')
                ui.space()
                ui.button('Join', on_click=save_user).classes('self-center')
