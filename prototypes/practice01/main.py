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

from prototypes.practice01.views import MemorizationView

UNSAFE_SECRET_KEY = 'UNSAFE_jsn9wx-vje-+#k%(b*kra1std2^v43^jtq&)5x26whm'

# Things I would like to implement:
#
# * Dutch to English -- select words
# * English to Dutch -- select words
# * Just Dutch -- select words
# * Free-form typing
#
# With TTS

def startup():
    @ui.page('/')
    async def home():
        view = MemorizationView()
        await view.display()


app.on_startup(startup)


if __name__ in ('__main__', '__mp_main__'):
    ui.run(favicon='💬', storage_secret=UNSAFE_SECRET_KEY)
