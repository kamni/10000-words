"""
Copyright (C) J Leadbetter <j@jleadbetter.com>
Affero GPL v3
"""

from typing import Any, Optional

from nicegui import app, ui

from common.ports.auth import AuthInvalidError
from frontend.widgets.base import BaseWidget
from frontend.widgets.errors import Error500Widget


class RegistrationLinkWidget(BaseWidget):
    """
    Show a link to the registration page
    """

    def display(self):
        with ui.row().classes('self-center'):
            ui.label('No account?')
            ui.link('Register for 10,000 Words', '/register')


class LoginWidget(BaseWidget):
    """
    Log into the system
    """

    def display(self):
        # This shouldn't happen,
        # because this means we got here without configuring the app.
        if not self.settings.show_login:
            Error500Widget().display()
            return

        user_adapter = self.adapters.get('UserDBPort')
        auth_adapter = self.adapters.get('AuthPort')

        username = None
        password = None
        error = None

        def login():
            error.classes(add='hidden')
            error.text = ''
            try:
                userui = auth_adapter.login(
                    username.value,
                    password.value if password else None,
                )
            except AuthInvalidError as exc:
                if self.settings.show_password_field:
                    error.text = 'Invalid username or password.'
                else:
                    error.text = 'Invalid username.'
                error.classes(remove='hidden')
            else:
                self.user = userui
                ui.notify('Welcome!')
                self.emit_done()

        ui.on('keydown.enter', login)

        with ui.card().classes('absolute-center'):
            ui.label('Login').classes('text-3xl')
            ui.separator()

            if self.settings.show_user_select:
                users = user_adapter.get_all()
                if not users:
                    RegistrationLinkWidget().display()
                    return

                if len(users) == 1:
                    user = users[0]
                    username = ui.input(
                        'Username',
                        value=user.username,
                    ).classes('text-1xl')
                else:
                    options = {
                        user.username: user.username
                        for user in users
                    }
                    username = ui.select(
                        label='Username',
                        options=options,
                        with_input=True,
                    )
            else:
                username = ui.input('Username')

            if self.settings.show_password_field:
                password = ui.input(
                    'Password',
                    password=True,
                    password_toggle_button=True,
                )

            error = ui.label('').classes(
                'text-amber-600 text-center self-center height-fit hidden',
            )

            ui.separator()
            if self.settings.show_registration:
                RegistrationLinkWidget().display()
            ui.button('Log In', on_click=login).classes('self-center')
