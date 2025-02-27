#!/usr/bin/env python

"""
Copyright (C) J Leadbetter <j@jleadbetter.com>
Affero GPL v3
"""

import json
import os
import re
import sys
from pathlib import Path
from typing import Dict, List, Optional

import toml
from pydantic import ValidationError

PROJECT_DIR = Path(__file__).resolve().parent.parent.parent
if PROJECT_DIR.as_posix() not in sys.path:
    sys.path.append(PROJECT_DIR.as_posix())

from common.utils.languages import language_name_to_code
from prototypes.practice01.models import Document, Sentence, Word


DATA_DIR = Path(__file__).resolve().parent / 'data'


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
        attributes = self._get_attributes(lines, input_file)
        text = self._get_text(lines)

        # Output file setup
        if not output_file.exists():
            output_file.touch()
        with output_file.open('r') as outfile:
            existing_toml = toml.load(outfile)

        try:
            # We have to convert this to JSON first,
            # Otherwise the UUIDs won't serialize correctly.
            doc_json = json.dumps(existing_toml['document'])
            document = Document.model_validate_json(doc_json)
        except (KeyError, ValidationError):
            document = Document()

        # These will be overwritten each time the script is run.
        self._set_document_attrs(document, attributes)

        # This will try to respect existing sentences,
        # but will overwrite if they differ.
        self._set_sentences(document, text)

        self._set_translation_and_words_interactively(document)

        # We have to run this through JSON so the UUIDs serialize correctly.
        new_toml = {
            'document': json.loads(
                document.model_dump_json(exclude_defaults=True),
            ),
        }
        with output_file.open('w') as outfile:
            toml.dump(new_toml, outfile)

    def _edit_word(self, word):
        new_word = input('New word: ')
        word.text = new_word.lower()

    def _get_output_file(self, input_file: Path) -> Path:
        input_path, input_name = input_file.as_posix().rsplit(os.sep, 1)
        base_name = input_name.split('.')[0]
        output_file = Path(input_path).resolve() / f'{base_name}.toml'
        return output_file

    def _get_attributes(
            self, input_lines: List[str], file_path: Path,
        ) -> Dict[str, str]:
        filename = file_path.as_posix().rsplit(os.sep, 1)[1]
        attrs = {'filename': filename}
        for line in input_lines:
            line = line.strip()
            if not line.startswith(':'):
                return attrs
            key, value = line.split(':', 2)[1:]
            attrs[key.strip().lower()] = value.strip()

    def _get_text(self, input_lines: List[str]) -> List[str]:
        text = []
        for line in input_lines:
            line = line.strip()
            if line.startswith(':'):
                continue
            text.append(line)
        return text

    def _make_translation(self, text: str) -> Sentence:
        sentence = Sentence(
            language_code='en',
            text=text,
        )
        return sentence

    def _parse_words(self, sentence: Sentence) -> List[Word]:
        tokens = self._tokenize_sentence(sentence.text)
        words = []
        for token in tokens:
            word = Word(
                text=token.lower(),
                language_code='en',
                example_sentence_ids=[sentence.id],
            )
            words.append(word)
        return words

    def _print_divider(self):
        print('-----------------------------------')

    def _set_document_attrs(self, doc: Document, attrs: Dict[str, str]):
        doc.display_name = attrs.get('title', attrs.get('filename'))
        doc.author = attrs.get('author')
        language = attrs.get('language')
        if language:
            try:
                doc.language_code = language_name_to_code[language]
            except KeyError:
                pass
        return doc

    def _set_sentences(self, doc: Document, text: List[str]):
        sentences = []
        for idx, line in enumerate(text):
            try:
                existing_sentence = list(filter(
                    lambda x: x.ordering == idx + 1,
                    doc.sentences,
                ))[0]
            except IndexError:
                existing_sentence = None

            # NOTE: We intentionally keep blank lines
            # in order to maintain paragraph spacing
            if not existing_sentence or existing_sentence.text != line:
                sentences.append(
                    Sentence(
                        text=line,
                        language_code=doc.language_code,
                        ordering=idx + 1,
                    )
                )
            else:
                sentences.append(existing_sentence)

        doc.sentences = sentences
        return doc

    def _set_translation_and_words_interactively(self, document):
        try:
            # Do translations first.
            for sentence in document.sentences:
                if not sentence.text or sentence.enabled_for_study:
                    continue

                if not sentence.translations:
                    self._print_divider()
                    print(f'\n{sentence.text}\n')
                    self._print_divider()
                    translation = input('Translation (en): ')
                    sentence.translations.append(
                        self._make_translation(translation),
                    )

            # Then load words
            for sentence in document.sentences:
                # TODO: we need to get the display text here,
                # so we can keep track of words,
                # and we don't keep re-asking for sentences
                # TODO: suggest alternative words
                # that similar display text has used to speed up the process.
                continue

                if not sentence.text or sentence.enabled_for_study:
                    continue

                self._print_divider()
                print(f'\n{sentence.text}\n')
                self._print_divider()

                words = self._parse_words(sentence)
                for word in words:
                    if word.text in document.words:
                        document.words[word.text].example_sentence_ids.extend(
                            word.example_sentence_ids,
                        )
                        continue

                    while word.status == 'not_set':
                        self._print_divider()
                        print(f'Word: {word.text}\n')
                        print('1. Learn this word.')
                        print('2. Mark word as already learned.')
                        print('3. Ignore this word.')
                        print('4. Edit word.\n')
                        word_status = int(input('What would you like to do? '))

                        if word_status == 4:
                            self._edit_word(word)
                            continue

                        self._set_word_status(word, word_status)
                        document.words[word.text] = word

                # Once the sentence has been completely processed,
                # we can start studying it
                sentence.enabled_for_study = True
        except KeyboardInterrupt:
            # We need to save before we exit
            print()
            self._print_divider()
            print('Saving and exiting...')
            return

    def _set_word_status(self, word: Word, status: int):
        word_status = {
            1: 'to_learn',
            2: 'learned',
            3: 'ignored',
        }[status]
        word.status = word_status

    def _tokenize_sentence(self, text: str) -> List[str]:
        tokens = []

        sentence_bits = text.split(' ')
        for item in sentence_bits:
            item = item.strip()
            if not item or item.isdecimal() or item.isdigit():
                continue

            only_punctuation = re.compile(r"^[^\w]+$")
            before = re.compile(r"^([^\w]*)(.*)$")
            after = re.compile(r"([\w\-_]+('\w+)*)([^\w]*)$")

            if only_punctuation.match(item):
                continue

            _punctuation, rest_of_bit = before.match(item).groups()
            word, _ignored, _punctuation = after.match(rest_of_bit).groups()
            tokens.append(word)

        return tokens

if __name__ == '__main__':
    toml_creator = TOMLCreator()
    toml_creator.create(DATA_DIR / 'aflevering-070.txt')
