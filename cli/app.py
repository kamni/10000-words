"""
Copyright (C) J Leadbetter <j@jleadbetter.com>
Affero GPL v3
"""

import os
import sys

from textual.app import App
from textual.theme import BUILTIN_THEMES

from cli.views.edit import EditScreen
from cli.views.learn import LearnScreen
from cli.views.login import LoginScreen
from common.stores.auth import AuthStore



class TenThousandWordsApp(App):
    SCREENS = {
        'edit': EditScreen,
        'learn': LearnScreen,
    }

    _auth_store = None

    @property
    def auth_store(self):
        if not self._auth_store:
            self._auth_store = AuthStore()
        return self._auth_store


    def on_mount(self):
        self.theme = 'flexoki'

        self.install_screen(LoginScreen, 'login')
        self.push_screen('login')
