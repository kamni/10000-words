"""
Copyright (C) J Leadbetter <j@jleadbetter.com>
Affero GPL v3
"""

from nicegui import app

from frontend.views.base import BaseView
from frontend.widgets.register import RegistrationWidget


class RegisterView(BaseView):
    """
    Register a new user.
    """

    def setup(self) -> bool:
        if (
            not self.settings.show_registration
            or (self.user and self.user.authenticated)
        ):
            self.redirect = '/'
            return False

        self.next_url = '/'
        self.page_content.append(RegistrationWidget())
        return True
