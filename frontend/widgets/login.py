"""
Copyright (C) J Leadbetter <j@jleadbetter.com>
Affero GPL v3
"""

from typing import Any, Optional

from nicegui import app, ui

from common.ports.auth import AuthInvalidError
from common.stores.adapter import AdapterStore
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

    @property
    def user(self):
        return self.user_controller.get()

    @user.setter
    def user(self, user):
        self.user_controller.set(user)

    def display(self):
        # This shouldn't happen,
        # because this means we got here without configuring the app.
        if not self.settings.show_login:
            Error500Widget().display()
            return

        self.username = None
        self.password = None
        self.error = None

        ui.on('keydown.enter', self._login)

        with ui.card().classes('absolute-center'):
            ui.label('Login').classes('text-3xl')
            ui.separator()

            if self.settings.show_user_select:
                users = self.user_controller.get_all()
                if not users:
                    RegistrationLinkWidget().display()
                    return

                if len(users) == 1:
                    user = users[0]
                    self.username = ui.input(
                        'Username',
                        value=user.username,
                    ).classes('text-1xl')
                else:
                    options = {
                        user.username: user.username
                        for user in users
                    }
                    self.username = ui.select(
                        label='Username',
                        options=options,
                        with_input=True,
                    )
            else:
                self.username = ui.input('Username')

            if self.settings.show_password_field:
                self.password = ui.input(
                    'Password',
                    password=True,
                    password_toggle_button=True,
                )

            self.error = ui.label('').classes(
                'text-amber-600 text-center self-center height-fit hidden',
            )

            ui.separator()
            if self.settings.show_registration:
                RegistrationLinkWidget().display()

            ui.button('Log In', on_click=self._login).classes('self-center')

    def _login(self):
        auth_adapter = AdapterStore().get('AuthPort')

        self.error.classes(add='hidden')
        self.error.text = ''
        try:
            user = auth_adapter.login(
                self.username.value,
                self.password.value if self.password else None,
            )
        except AuthInvalidError as exc:
            if self.settings.show_password_field:
                self.error.text = 'Invalid username or password.'
            else:
                self.error.text = 'Invalid username.'
            self.error.classes(remove='hidden')
        else:
            self.user = user
            ui.notify('Welcome!')
            self.emit_done()

