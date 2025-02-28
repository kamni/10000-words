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
                if not sentence.text or sentence.translation:
                    continue

                self._print_divider()
                print(f'\n{sentence.text}\n')
                self._print_divider()
                translation = input('Translation (en): ')
                sentence.translation = self._make_translation(translation)

            # Then load words
            for sentence in document.sentences:
                # TODO: we need to get the display text here,
                # so we can keep track of words,
                # and we don't keep re-asking for sentences
                # TODO: suggest alternative words
                # that similar display text has used to speed up the process.
                if not sentence.text or sentence.enabled_for_study:
                    continue

                self._print_divider()
                print(f'\n{sentence.text}\n')
                self._print_divider()

                print(
                    'Which words or phrases would you like to learn? '
                    '(comma-separated)'
                )
                wordstr = input()
                wordtext = [
                    word.strip() for word in wordstr.split(',')
                    if word.strip()
                ]
                words = []
                for word in wordtext:
                    translation = input(f'Translation for "{word}": ').strip()
                    word = Word(
                        text=word,
                        language_code='nl',
                        enabled_for_study=True,
                        translation=Word(
                            text=translation,
                            language_code='en',
                        ),
                    )
                    words.append(word)

                # Update words
                for word in words:
                    try:
                        existing_word = document.words.pop(
                            document.words.index(word),
                        )
                    except ValueError:
                        document.words.append(word)
                        continue

                    self._print_divider()
                    print('You have duplicate words:\n')
                    print(f'1. {word.text}: {word.translation.text}')
                    print(
                        f'2. {existing_word.text}: '
                        f'{existing_word.translation.text}'
                    )
                    print('3. Combine them\n')

                    answer = None
                    while answer not in ('1', '2', '3'):
                        answer = input('Which one would you like to keep? ')

                    if answer == '3':
                        new_translation = input(
                            'What would you like the translation to be? ',
                        )
                        word.translation = Word(
                            text=new_translation,
                            language_code='en',
                        )
                    elif answer == '2':
                        word = existing_word

                    document.words.append(word)

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

'''
    def make_mp3(
        sentence: Dict,
        tts_dir: Path,
        idx: int,
        download_tts_again: bool,
    ) -> Path:
        counter = str(idx).zfill(3)
        mp3_filename = f'{counter}.mp3'
        mp3 = tts_dir / mp3_filename

        if not mp3.exists() or download_tts_again:
            print(f'Downloading {mp3_filename}...')
            tts = gTTS(sentence['text'], lang='nl')
            tts.save(mp3.as_posix())
        else:
            print(f'Skipping download of {mp3_filename}. Already downloaded.')
        return mp3
'''

if __name__ == '__main__':
    toml_creator = TOMLCreator()
    toml_creator.create(DATA_DIR / 'aflevering-070.txt')
