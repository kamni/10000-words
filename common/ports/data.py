"""
Copyright (C) J Leadbetter <j@jleadbetter.com>
Affero GPL v3
"""

import json
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Optional, Union

import toml
from pydantic import ValidationError
from toml.decoder import TomlDecodeError

from ..models.database import Database
from ..utils.files import get_project_dir


class DataLoadError(Exception):
    """
    Indicates that an error occurred while loading data from a file.
    """
    pass


class DataExportError(Exception):
    """
    Indicates that an error occured while dumping data to a file.
    """
    pass


class DataPort(ABC):
    """
    Handles loading data into the database from a database dump.

    NOTE: The preferred format here is TOML, not JSON, because of readability.
    """

    @abstractmethod
    def load(self, data_file: Optional[Path]=None):
        """
        Load data from a TOML file into the database.

        :data_file: Path to the file that should be loaded.
            If not specified, defaults to
            `dev.in_memory.stores.datastore.DataFile` in `setup.cfg`.
        """
        pass

    @abstractmethod
    def export(self, data_file: Optional[Path]=None):
        """
        Export data to a TOML file from the database.

        :data_file: Path to the file to write the data to.
            If not specified, defaults to
            `dev.in_memory.stores.datastore.DataFile` in `setup.cfg`.
        """
        pass

    def get_filepath(self, filename: Optional[str]=None) -> Union[Path, None]:
        """
        Get the Path for the given file name.

        :filename: string representing the filename.
            If not supplied, this method will return None.

        :return: Path or None, if filename was not provided.
        """
        if filename is None:
            return None
        elif filename.startswith('/'):
            return Path(filename)
        else:
            return get_project_dir() / filename

    def get_data(self, data_file: Path) -> Database:
        """
        Get the data stored in the database file.

        :data_file: Path to the TOML file to read.

        :return: Database object that can be used for further database setup.
        :raises: DataLoadError if something goes wrong.
        """
        try:
            with data_file.open('r') as datafile:
                data = toml.load(datafile)

            # We have to go through JSON to ensure correct serialization
            json_data = json.dumps(data)
            db = Database.model_validate_json(json_data)
            return db
        except (
            AttributeError,
            FileNotFoundError,
            OSError,
            TomlDecodeError,
            ValidationError,
        ) as exc:
            filename = data_file.as_posix() if data_file else None
            raise DataLoadError(
                f'Could not load data from file {filename}: {exc}'
            )

    def write_data(self, database: Database, data_file: Path):
        """
        Write the Database object to the specified file.

        :database: A pydantic Database object to convert to TOML.
        :data_file: Where the TOML should be written.

        :raises: DataExportError if something goes wrong.
        """
        # We have to convert this to JSON first
        # so it serializes the UUIDs correctly.
        json_data = database.model_dump_json(exclude_defaults=True)
        toml_dict = json.loads(json_data)

        try:
            with data_file.open('w') as datafile:
                toml.dump(toml_dict, datafile)
        except (AttributeError, OSError) as exc:
            filename = data_file.as_posix() if data_file else None
            raise DataExportError(
                f'Could not export data to file {filename}: {exc}'
            )
