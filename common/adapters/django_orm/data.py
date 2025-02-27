"""
Copyright (C) J Leadbetter <j@jleadbetter.com>
Affero GPL v3
"""

from pathlib import Path
from typing import Optional

from ...models.database import Database
from ...ports.data import DataPort
from ...stores.adapter import AdapterStore


class DataDjangoORMAdapter(DataPort):
    """
    Handle data in a Django-managed database.
    """

    def __init__(self, **kwargs):
        self.data_file = self.get_filepath(kwargs.get('datafile'))
        self._adapters = None

    @property
    def adapters(self):
        if not self._adapters:
            self._adapters = AdapterStore()
        return self._adapters

    def load(self, data_file: Optional[Path]=None):
        """
        Load data from a TOML file into the database.

        :data_file: Path to the file that should be loaded.
            If not specified, defaults to
            `dev.in_memory.stores.datastore.DataFile` in `setup.cfg`.
        """
        db = self.get_data(data_file or self.data_file)

        app_settings = self.adapters.get('AppSettingsDBPort')
        if db.app_settings:
            app_settings.create_or_update(db.app_settings)

        userdb = self.adapters.get('UserDBPort')
        new_userdbs: Dict[uuid.UUID, UserDB] = {}
        for user in db.users:
            old_id = user.id
            new_user = userdb.create(user, ignore_errors=True)
            new_userdbs[old_id] = new_user

        documentdb = self.adapters.get('DocumentDBPort')
        for doclist in db.documents.values():
            for doc in doclist:
                new_userdb_id = new_userdbs[doc.user_id].id
                doc.user_id = new_userdb_id
                documentdb.create_or_update(doc)

    def export(self, data_file: Optional[Path]=None):
        """
        Export data to a TOML file from the database.

        :data_file: Path to the file to write the data to.
            If not specified, defaults to
            `dev.in_memory.stores.datastore.DataFile` in `setup.cfg`.
        """
        db = Database()

        app_settings = self.adapters.get('AppSettingsDBPort')
        db.app_settings = app_settings.get()

        userdb = self.adapters.get('UserDBPort')
        db.users = userdb.get_all()

        documentdb = self.adapters.get('DocumentDBPort')
        for user in db.users:
            db.documents[str(user.id)] = documentdb.get_all(user.id)

        self.write_data(db, data_file or self.data_file)
