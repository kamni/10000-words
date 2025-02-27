"""
Copyright (C) J Leadbetter <j@jleadbetter.com>
Affero GPL v3
"""

from typing import Dict, Optional

from nicegui import ui
from nicegui.elements.label import Label

from common.models.settings import AppSettingsDB
from frontend.widgets.base import BaseWidget


class OptionWidget(BaseWidget):
    """
    Display an individual configuration option
    """

    def __init__(self, text: str, value: bool, marker: str):
        super().__init__()

        self._text = text
        self._value = value
        self._marker = marker

    @property
    def value(self) -> bool:
        return self.switch.value

    def display(self):
        def update_no_and_yes():
            value = self.switch.value
            no = self.no
            yes = self.yes

            if value:
                yes.classes(add='outline')
                no.classes(remove='outline')
            else:
                no.classes(add='outline')
                yes.classes(remove='outline')

        ui.label(self._text).classes('text-lg')
        self.no = ui.label('no').classes('text-right text-negative text-lg px-4')
        self.switch = ui.switch(
            value=self._value,
            on_change=update_no_and_yes,
        ).mark(self._marker)
        self.yes = ui.label('yes').classes('text-left text-positive text-lg px-4')

        update_no_and_yes()


class ConfigureWidget(BaseWidget):
    """
    Configure the global app settings
    """

    @property
    def settings(self):
        return self.settings_controller.get()

    @settings.setter
    def settings(self, settings_dict: Dict[str, bool]):
        self.settings_controller.update(settings_dict)

    def display(self):
        is_configured = self.settings.is_configured
        current_db_settings = self.settings_controller.get_db()

        self._multiuser = OptionWidget(
            'Can multiple people use the app?',
            current_db_settings.multiuser_mode,
            'multiuser',
        )
        self._passwordless = OptionWidget(
            'Log in without a password?',
            current_db_settings.passwordless_login,
            'passwordless',
        )
        self._show_users = OptionWidget(
            'Show user list on the login page?',
            current_db_settings.show_users_on_login_screen,
            'show-user',
        )

        with ui.card().classes('absolute-center'):
            ui.label('Settings').classes('text-3xl')
            ui.separator()

            with ui.grid(columns='auto auto auto auto'):
                self._multiuser.display()
                self._passwordless.display()
                self._show_users.display()

            ui.separator()
            with ui.row().classes('w-full'):
                if is_configured:
                    ui.button('Cancel', on_click=self.emit_cancel, color='warning')
                ui.space()
                ui.button('Save', on_click=self._save_settings)

    def _save_settings(self):
        self.settings = {
            'multiuser_mode': self._multiuser.value,
            'passwordless_login': self._passwordless.value,
            'show_users_on_login_screen': self._show_users.value,
        }
        ui.notify('Settings Saved!')
        self.emit_done()

