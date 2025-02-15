"""
Copyright (C) J Leadbetter <j@jleadbetter.com>
Affero GPL v3
"""

import uuid
from pathlib import Path
from typing import Dict, Optional

from ..models.database import Database
from ..models.documents import DocumentDB
from ..models.settings import AppSettingsDB
from ..models.users import UserDB
from ..stores.app import AppStore
from ..utils.files import get_project_dir


PROJECT_DIR = Path(get_project_dir())
DATA_FILE = PROJECT_DIR / 'scripts' / 'data' / 'db.json'


class DataLoader:
    """
    Load data into a database.

    WARNING: May delete the existing ConfigStore.
        Do not run this while the server is live and in production.
    """

    def __init__(
        self,
        config: Optional[str]=None,
        subsection: Optional[str]=None,
        force_config: Optional[bool]=False,
    ):
        # NOTE: ConfigStore is a singleton.
        # If it has already been initialized
        # the settings passed to __init__ will be ignored
        # unless force_config_reinitialization is True
        if force_config:
            AppStore.destroy_all()

        # NOTE: The setup.cfg file has a setting LoadTestData.
        # The script assumes you know what you're doing,
        # So it runs even if LoadTestData = no
        # if you've called this script manually.
        app_store = AppStore(config, subsection)
        self.config = app_store.get('ConfigStore')
        self.adapters = app_store.get('AdapterStore')

    def load(self):
        """
        Load a database with data from scripts/data/db.json
        """

        json_text=''
        with open(DATA_FILE, 'r') as data_file:
            json_text = data_file.read()

        database = Database.model_validate_json(json_text)

        app_settings = self.adapters.get('AppSettingsDBPort')
        app_settings.create_or_update(database.app_settings)

        userdb = self.adapters.get('UserDBPort')
        new_userdbs: Dict[uuid.UUID, UserDB] = {}
        for user in database.users:
            old_id = user.id
            new_user = userdb.create(user, ignore_errors=True)
            new_userdbs[old_id] = new_user

        documentdb = self.adapters.get('DocumentDBPort')
        for doc in database.documents:
            new_userdb_id = new_userdbs[doc.user_id].id
            doc.user_id = new_userdb_id
            documentdb.create_or_update(doc)
