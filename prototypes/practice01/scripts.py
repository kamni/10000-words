#!/usr/bin/env python

"""
Copyright (C) J Leadbetter <j@jleadbetter.com>
Affero GPL v3
"""

import os
import sys
from pathlib import Path
from typing import Optional

PROJECT_DIR = Path(__file__).resolve().parent.parent.parent
if PROJECT_DIR.as_posix() not in sys.path:
    sys.path.append(PROJECT_DIR.as_posix())

DATA_DIR = Path(__file__).resolve().parent / 'data'


class TOMLCreator:
    """
    Takes a text file and turns it into a TOML file.
    """

    def create(self, input_file: Path, output_file: Optional[Path]=None):
        """
        Creates a toml file from a text document.

        :input_file: The text document.
        :output_file: Where the TOML should be written.
            If not specified, defaults to the name of the input file,
            with the extension `toml`.
        """
        if not output_file:
            output_file = self._get_output_file(input_file)
        print(output_file.as_posix())

    def _get_output_file(self, input_file: Path) -> Path:
        input_path, input_name = input_file.as_posix().rsplit(os.sep, 1)
        base_name = input_name.split('.')[0]
        output_file = Path(input_path).resolve() / f'{base_name}.toml'
        return output_file


if __name__ == '__main__':
    toml_creator = TOMLCreator()
    toml_creator.create(DATA_DIR / 'aflevering-071.txt')
