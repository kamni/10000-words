#!/usr/bin/env python

import argparse
import os
import random
from pathlib import Path
from typing import Any, Dict, List, Optional

import genanki
import toml


PROJECT_DIR = Path(__file__).resolve().parent.parent
INPUT = PROJECT_DIR / 'practice01' / 'data' / 'aflevering-070.toml'


class AnkiDeckCreator:
    """
    Generate Anki decks from TOML files
    """

    def create(
        self,
        input_file: Path,
    ):
        doc_dict = self.import_toml_file(input_file)
        self.create_sentence_deck(doc_dict, input_file)
        self.create_vocabulary_deck(doc_dict, input_file)

    def create_sentence_deck(self, doc_dict: Dict[str, Any], input_file: Path):
        output_file = self.get_output_file(input_file)

        model = self.make_anki_sentence_model(input_file.stem)
        deck = self.make_anki_deck(doc_dict['display_name'])
        package = self.make_anki_package(deck)

        self.add_notes(doc_dict['sentences'], 'sentence', deck, model)
        self.write_to_file(package, output_file)

    def create_vocabulary_deck(self, doc_dict: Dict[str, Any], input_file: Path):
        output_file = self.get_output_file(input_file, '-vocabulary')

        model = self.make_anki_vocabulary_model(input_file.stem)
        deck = self.make_anki_deck('Vocabulary: ' + doc_dict['display_name'])
        package = self.make_anki_package(deck)

        self.add_notes(doc_dict['words'], 'word', deck, model)
        self.write_to_file(package, output_file)

    def add_notes(
        self,
        items: List[Any],
        item_type: str,
        deck: genanki.Deck,
        model: genanki.Model,
    ):
        for idx, item in enumerate(items):
            if not item['text'] or not item.get('enabled_for_study'):
                continue

            note = genanki.Note(
                model=model,
                fields=[
                    item['text'],
                    item['translation']['text'],
                ],
            )
            deck.add_note(note)
            print(f'Added note for {item_type} "{item["text"]}".')
            print('------------------------')

    def get_output_file(self, input_file: Path, affix: Optional[str]='') -> Path:
        base_path = input_file.as_posix().rsplit(os.sep, 1)[0]
        base_name = input_file.stem
        new_path = Path(base_path) / f'{base_name}{affix}.apkg'
        return new_path

    def import_toml_file(self, input_file: Path):
        with input_file.open('r') as infile:
            doc_dict = toml.load(infile)
        return doc_dict['document']

    def make_anki_sentence_model(self, id_seed: str) -> genanki.Model:
        # We want this to be reproduceable
        random.seed(id_seed)
        model_id = random.randrange(1 << 30, 1 << 31)

        tts = 'tts nl_NL voices=com.google.android.tts-nl-nl-x-lfc-local'
        model = genanki.Model(
            model_id,
            '10,000 Words Model',
            fields=[
                {'name': 'Dutch'},
                {'name': 'English'},
            ],
            templates=[
                {
                    'name': 'Dutch-To-English',
                    'qfmt': (
                        '{{Dutch}}<br>{{' + tts + ':Dutch}}<br><br>'
                        '{{type:English}}'
                    ),
                    'afmt': '{{FrontSide}}<hr id="answer">{{English}}',
                },
                {
                    'name': 'English-to-Dutch',
                    'qfmt': '{{English}}<br><br>{{type:Dutch}}',
                    'afmt': '{{FrontSide}}<hr id="answer">{{' + tts + ':Dutch}}',
                },
                {
                    'name': 'Dutch-Listening',
                    'qfmt': '{{' + tts + ':Dutch}}<br><br>{{type:Dutch}}',
                    'afmt': '{{FrontSide}}<hr id="answer">{{Dutch}}',
                },
            ],
        )
        return model

    def make_anki_vocabulary_model(self, id_seed: str) -> genanki.Model:
        # We want this to be reproduceable
        random.seed(f'{id_seed}-vocabulary')
        model_id = random.randrange(1 << 30, 1 << 31)

        tts = 'tts nl_NL voices=com.google.android.tts-nl-nl-x-lfc-local'
        model = genanki.Model(
            model_id,
            '10,000 Words Vocabulary Model',
            fields=[
                {'name': 'Dutch'},
                {'name': 'English'},
            ],
            templates=[
                {
                    'name': 'Dutch-To-English',
                    'qfmt': (
                        '{{Dutch}}<br>{{' + tts + ':Dutch}}<br><br>'
                        '{{type:English}}'
                    ),
                    'afmt': '{{FrontSide}}<hr id="answer">{{English}}',
                },
                {
                    'name': 'English-to-Dutch',
                    'qfmt': '{{English}}<br><br>{{type:Dutch}}',
                    'afmt': '{{FrontSide}}<hr id="answer">{{' + tts + ':Dutch}}',
                },
            ],
        )
        return model

    def make_anki_deck(self, deck_name: str):
        random.seed(deck_name)
        deck_id = random.randrange(1 << 30, 1 << 31)

        deck = genanki.Deck(deck_id, deck_name)
        return deck

    def make_anki_package(self, deck: genanki.Deck) -> genanki.Package:
        package = genanki.Package(deck)
        return package

    def write_to_file(self, package: genanki.Package, filepath: Path):
        print('Writing to file...')
        package.write_to_file(filepath.as_posix())
        print('Done!\n')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        prog='CreateAnki',
        description=(
            'Create an Anki .apkg file from TOML configuration.'
        ),
    )
    parser.add_argument(
        '-i',
        '--input-file',
        default=INPUT.as_posix(),
        help='Path to the TOML file you want to load.',
    )
    args = parser.parse_args()

    anki = AnkiDeckCreator()
    anki.create(Path(args.input_file))
