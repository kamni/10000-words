"""
Copyright (C) J Leadbetter <j@jleadbetter.com>
Affero GPL v3
"""

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
        if not self._app_settings.show_login:
            Error500Widget().display()
            return

        user_adapter = self._adapters.get('UserDBPort')
        auth_adapter = self._adapters.get('AuthPort')

        self._username = None
        self._password = None
        self._error = None

        def login():
            self._error.classes(add='hidden')
            self._error.text = ''
            try:
                userui = auth_adapter.login(
                    self._username.value,
                    self._password.value if self._password else None,
                )
            except AuthInvalidError as exc:
                if self._app_settings.show_password_field:
                    self._error.text = 'Invalid username or password.'
                else:
                    self._error.text = 'Invalid username.'
                self._error.classes(remove='hidden')
            else:
                app.storage.user.update(userui.model_dump())
                app.storage.user['authenticated'] = True
                ui.notify('Welcome!')
                self.emit_done()

        with ui.card().classes('absolute-center'):
            ui.label('Login').classes('text-3xl')
            ui.separator()

            if self._app_settings.show_user_select:
                users = user_adapter.get_all()
                if not users:
                    RegistrationLinkWidget().display()
                    return

                if len(users) == 1:
                    user = users[0]
                    self._username = ui.input(
                        'Username',
                        value=user.username,
                    ).classes('text-1xl')
                else:
                    options = {
                        user.username: user.username
                        for user in users
                    }
                    self._username = ui.select(
                        label='Username',
                        options=options,
                        with_input=True,
                    )
            else:
                self._username = ui.input('Username')

            if self._app_settings.show_password_field:
                self._password = ui.input('Password', password=True)

            self._error = ui.label('').classes(
                'text-amber-600 text-center self-center height-fit hidden',
            )

            ui.separator()
            if self._app_settings.show_registration:
                RegistrationLinkWidget().display()
            ui.button('Log In', on_click=login).classes('self-center')
