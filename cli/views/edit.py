"""
Copyright (C) J Leadbetter <j@jleadbetter.com>
Affero GPL v3
"""

from textual.app import ComposeResult
from textual.screen import Screen
from textual.widgets import Static


class EditScreen(Screen):
    BINDINGS = [('escape', 'app.pop_screen', 'Back')]

    def compose(self) -> ComposeResult:
        yield Static('Editing')
