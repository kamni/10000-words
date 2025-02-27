"""
Copyright (C) J Leadbetter <j@jleadbetter.com>
Affero GPL v3
"""

from collections.abc import Callable

from frontend.widgets.base import BaseWidget

from nicegui import app, ui


class HeaderLink(BaseWidget):
    """
    Display a link to a page in the header
    """

    def __init__(self, text: str, path: str):
        super().__init__()
        self._text = text
        self._path = path

    def display(self):
        ui.link(self._text, self._path).classes(
            'text-2xl text-zinc-50 no-underline',
        )
        ui.label('|').classes('text-2xl pr-5 pl-5')


class MenuButton(BaseWidget):
    """
    Button in the right sidebar menu
    """

    def __init__(self, text: str, icon: str, on_click=Callable):
        self._text = text
        self._icon = icon
        self._on_click = on_click

    def display(self):
        ui.button(
            self._text,
            icon=self._icon,
            on_click=self._on_click,
        ).classes(
            'w-full !text-zinc-700 text-lg',
        ).props('flat color=white')


class Header(BaseWidget):
    """
    Displays a header on the page
    """

    def display(self):
        user = self.user
        user_authenticated = user and user.authenticated
        app_is_configured = self.settings.is_configured
        show_logout = self.settings.show_logout and user_authenticated
        show_settings = user and user.isAdmin

        with ui.header():
            ui.label('💬').classes('text-2xl')
            ui.label('10,000 Words').classes('text-2xl')
            ui.space()
            if user_authenticated and app_is_configured:
                HeaderLink('Edit', '/edit').display()
                HeaderLink('Practice', '/practice').display()

                if show_logout or show_settings:
                    with ui.button(
                        on_click=lambda: right_drawer.toggle(),
                    ).mark('header-user-menu').props('flat color=white'):
                        ui.label(user.displayName).classes('text-xl pr-3')
                        ui.icon('account_circle').classes('text-xl pl-2')
                else:
                    ui.label(user.displayName).mark('header-username') \
                            .classes('text-2xl')

        if show_logout or show_settings:
            with ui.right_drawer().classes('bg-secondary') as right_drawer:
                right_drawer.hide()

                if show_settings:
                    MenuButton(
                        'App Settings',
                        'settings',
                        lambda: ui.navigate.to('/configure'),
                    ).display()

                    if show_logout:
                        ui.separator()

                if show_logout:
                    MenuButton('Logout', 'logout', self._logout).display()

    def _logout(self):
        self.user_controller.reset()
        ui.navigate.to('/')
