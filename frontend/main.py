"""
Copyright (C) J Leadbetter <j@jleadbetter.com>
Affero GPL v3
"""

import sys
from pathlib import Path
from typing import Optional

from nicegui import app, ui

BASE_DIR = Path(__file__).resolve().parent
PROJECT_DIR = BASE_DIR.parent

if BASE_DIR.as_posix() not in sys.path:
    sys.path.append(BASE_DIR.as_posix())
if PROJECT_DIR.as_posix() not in sys.path:
    sys.path.append(PROJECT_DIR.as_posix())

from common.stores.config import ConfigStore

from frontend.middleware.auth import AuthMiddleware
from frontend.views.configure import ConfigureView
from frontend.views.edit import EditView
from frontend.views.login import LoginView
from frontend.views.register import RegisterView


UNSAFE_SECRET_KEY = 'UNSAFE_jsn9wx-vje-+#k%(b*kra1std2^v43^jtq&)5x26whm'


def startup(config: Optional[str]=None, subsection: Optional[str]=None):
    """
    Set up configuration from setup.cfg

    :config: Path to configuration file.
        If not specified, uses the top-level setup.cfg.
    :subsection: Subsection of the config file to use (e.g., 'dev.django').
        If not specified, uses the `common.meta.DefaultConfig` value.
    """

    # Initialize the configuration.
    # ConfigStore is a singleton that lasts for the duration of the app.
    ConfigStore(config=config, subsection=subsection)

    @ui.page('/')
    async def login():
        ui.page_title('Login')
        view = LoginView()
        return await view.display()

    @ui.page('/configure')
    async def configure():
        ui.page_title('Configure Settings')
        view = ConfigureView()
        return await view.display()

    @ui.page('/register')
    async def register():
        ui.page_title('Register')
        view = RegisterView()
        return await view.display()

    @ui.page('/edit')
    async def edit():
        ui.page_title('Editing Mode')
        view = EditView()
        return await view.display()

    @ui.page('/practice')
    def practice():
        ui.page_title('Practice Mode')
        ui.label('practice')


app.add_middleware(AuthMiddleware)
app.on_startup(startup)


if __name__ in {'__main__', '__mp_main__'}:
    ui.run(favicon='💬', storage_secret=UNSAFE_SECRET_KEY)
