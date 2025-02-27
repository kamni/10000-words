"""
Copyright (C) J Leadbetter <j@jleadbetter.com>
Affero GPL v3
"""

from nicegui import app

from frontend.controllers.documents import DocumentController
from frontend.views.base import BaseView
from frontend.widgets.edit import EditWidget


class EditView(BaseView):
    """
    Add and edit text to practice with
    """

    def set_storage(self):
        """
        Set data needed by the widgets.
        This will be available to all widgets.
        """
        controller = DocumentController()
        controller.set(self.user)

    def setup(self):
        self.page_content.append(EditWidget())
