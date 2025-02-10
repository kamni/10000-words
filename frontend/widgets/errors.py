"""
Copyright (C) J Leadbetter <j@jleadbetter.com>
Affero GPL v3
"""

from nicegui import ui

from frontend.widgets.base import BaseWidget


class Error500Widget(BaseWidget):
    """
    Displays an error message
    """

    def display(self):
        with ui.card().classes('absolute-center'):
            ui.label('Oops!').classes('text-3xl text-amber-600')
            ui.separator()
            ui.label('Something went wrong.').classes('text-2xl')
            ui.label('Please contact your administrator.').classes('text-2xl')
