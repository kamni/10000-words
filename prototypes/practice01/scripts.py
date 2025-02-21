#!/usr/bin/env python

"""
Copyright (C) J Leadbetter <j@jleadbetter.com>
Affero GPL v3
"""

import os
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

import toml
from pydantic import BaseModel

PROJECT_DIR = Path(__file__).resolve().parent.parent.parent
if PROJECT_DIR.as_posix() not in sys.path:
    sys.path.append(PROJECT_DIR.as_posix())

from common.utils.languages import LanguageCode, language_name_to_code


DATA_DIR = Path(__file__).resolve().parent / 'data'


class Document(BaseModel):
    display_name: str
    author: Optional[str] = None
    language_code: Optional[LanguageCode] = 'en'
    sentences: Optional[List['Sentence']] = []


class TOMLCreator:
    """
    Takes a text file and turns it into a TOML file.
    Can be exited and re-run.
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

        # Input file setup
        with input_file.open('r') as infile:
            lines = infile.readlines()
        attributes = self._get_attributes(lines)
        text = self._get_text(lines)

        # Output file setup
        if not output_file.exists():
            output_file.touch()
        with output_file.open('r') as outfile:
            existing_toml = toml.load(outfile)

        '''
        # These will be redone each time the script is run.
        self._setup_toml_dict(existing_toml)
        self._set_title(attributes, existing_toml)
        self._set_author(attributes, existing_toml)
        self._set_language(attributes, existing_toml)

        # This will try to respect existing sentences
        self._set_sentences(text, existing_toml)
        '''

        print(existing_toml)
        print(text)
        print(attributes)

    def _get_output_file(self, input_file: Path) -> Path:
        input_path, input_name = input_file.as_posix().rsplit(os.sep, 1)
        base_name = input_name.split('.')[0]
        output_file = Path(input_path).resolve() / f'{base_name}.toml'
        return output_file

    def _get_attributes(self, input_lines: List[str]) -> Dict[str, str]:
        attrs = {}
        for line in input_lines:
            line = line.strip()
            if not line.startswith(':'):
                return attrs
            key, value = line.split(':', 2)[1:]
            attrs[key.strip()] = value.strip()

    def _get_text(self, input_lines: List[str]) -> List[str]:
        text = []
        for line in input_lines:
            line = line.strip()
            if line.startswith(':'):
                continue
            text.append(line)
        return text

    def _setup_toml_dict(self, toml: Dict[str, Any]):
        if 'document' not in toml:
            toml['document'] = {}
        if 'sentences' not in toml['document']:
            toml['document']['sentences'] = []

    def _set_title(self, title: str, toml: Dict[str, Any]):
        toml['document']['display_name'] = title

    def _set_author(self, author: str, toml: Dict[str, Any]):
        toml['document']['author'] = author

    def _set_language(self, language: str, toml: Dict[str, Any]):
        toml['document']['language_code'] = language_name_to_code[language]

    def _set_sentences(self, sentences: List[str], toml: Dict[str, Any]):
        pass


if __name__ == '__main__':
    toml_creator = TOMLCreator()
    toml_creator.create(DATA_DIR / 'aflevering-071.txt')
