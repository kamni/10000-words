"""
Copyright (C) J Leadbetter <j@jleadbetter.com>
Affero GPL v3
"""

import os
import sys

TOP_LEVEL_FOLDER = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if not TOP_LEVEL_FOLDER in sys.path:
    sys.path.append(TOP_LEVEL_FOLDER)

from cli.app import TenThousandWordsApp


app = TenThousandWordsApp()
app.run()
