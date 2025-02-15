"""
Copyright (C) J Leadbetter <j@jleadbetter.com>
Affero GPL v3
"""

import sys
from pathlib import Path

from nicegui import app, ui

PROJECT_DIR = Path(__file__).resolve().parent.parent.parent
if PROJECT_DIR.as_posix() not in sys.path:
    sys.path.append(PROJECT_DIR.as_posix())

from common.stores.app import AppStore

from prototypes.edit01.views import Edit01View

UNSAFE_SECRET_KEY = 'UNSAFE_jsn9wx-vje-+#k%(b*kra1std2^v43^jtq&)5x26whm'


def startup():
    app_store = AppStore(subsection='dev.in_memory')

    @ui.page('/')
    async def login():
        ui.page_title('Edit')
        view = Edit01View()
        await view.display()


app.on_startup(startup)


if __name__ in {'__main__', '__mp_main__'}:
    ui.run(favicon='💬', storage_secret=UNSAFE_SECRET_KEY)

