"""
Copyright (C) J Leadbetter <j@jleadbetter.com>
Affero GPL v3

The Pydantic models in the module are dynamicall created at time of use.
Each language has its own configuration,
located in common.models.config/<language_code>.py.
"""

import importlib
import sys
import uuid
from enum import Enum
from functools import partial
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, create_model

class DefaultGrammarType(str, Enum):
    # Prepositions are not included here,
    # because prepositions are difficult to learn
    # without the context of the verb.
    # If your use case requires prepositions or other unlisted types,
    # please create your own model with `make_grammar_model`
    unknown = 'unknown'
    noun = 'noun'
    pronoun = 'pronoun'
    adjective = 'adjective'
    adverb = 'adverb'
    verb = 'verb'
    participle = 'participle'
    conjunction = 'conjunction'


# We use camelCase in the config
# so that we can easily export to javascript in the frontend
DEFAULT_CONFIG = {
    'UnknownData': {
        'id': (Optional[str], None),
        'text': (str, ...),
    },
    'Unknown': {
        'id': (Optional[str], None),
        'type': ('DefaultGrammarType', DefaultGrammarType.unknown),
        'data': (list, ...)  # UnknownData; pydantic complains if we type the list
    },
    'NounData': {
        'id': (Optional[str], None),
        'case': ('DefaultCase', ...),
        'plurality': ('DefaultPlurality', ...),
        'gender': ('DefaultGender', ...),
        'article': (str, ...),
        'text': (str, ...),
    },
    'Noun': {
        'id': (Optional[str], None),
        'type': ('DefaultGrammarType', DefaultGrammarType.unknown),
        'data': (list, ...),  # NounData; pydantic complains...
    },
    'PronounData': {
        'id': (Optional[str], None),
        'case': ('DefaultCase', ...),
        'gender': ('DefaultGender', ...),
        'politeness': ('DefaultPoliteness', ...),
        'text': (str, ...),
    },
    'Pronoun': {
        'id': (Optional[str], None),
        'type': ('DefaultGrammarType', DefaultGrammarType.unknown),
        'data': (list, ...),  # PronounData; pydantic complains...
    },
    'AdjectiveData': {
        'id': (Optional[str], None),
        'case': ('DefaultCase', ...),
        'gender': ('DefaultGender', ...),
        'text': (str, ...),
    },
    'Adjective': {
        'id': (Optional[str], None),
        'type': ('DefaultGrammarType', DefaultGrammarType.unknown),
        'data': (list, ...),  # AdjectiveData; pydantic complains...
    },
    'AdverbData': {
        'id': (Optional[str], None),
        'text': (str, ...),
    },
    'Adverb': {
        'id': (Optional[str], None),
        'type': ('DefaultGrammarType', DefaultGrammarType.unknown),
        'data': (list, ...),  # AdverbData; pydantic complains...
    },
    'VerbData': {
        'id': (Optional[str], None),
        'tense': (str, ...),
        'person': ('DefaultPerson', ...),
        'gender': ('DefaultGender', ...),
        'politeness': ('DefaultPoliteness', ...),
        'text': (str, ...),
    },
    'Verb': {
        'id': (Optional[str], None),
        'type': ('DefaultGrammarType', DefaultGrammarType.unknown),
        'data': (list, ...),  # VerbData; pydantic complains...
    },
    'ParticipleData': {
        'id': (Optional[str], None),
        'relatedVerb': (str, ...),
        'text': (str, ...),
    },
    'Participle': {
        'id': (Optional[str], None),
        'type': ('DefaultGrammarType', DefaultGrammarType.unknown),
        'data': (list, ...),  # ParticipleData; pydantic complains...
    },
    'ConjunctionData': {
        'id': (Optional[str], None),
        'text': (str, ...),
    },
    'Conjunction': {
        'id': (Optional[str], None),
        'type': ('DefaultGrammarType', DefaultGrammarType.unknown),
        'data': (list, ...),  # ConjunctionData; pydantic complains...
    },
}


class DefaultCase(str, Enum):
    nominative = 'nominative'
    accusative = 'accusative'
    dative = 'dative'
    genitive = 'genitive'


class DefaultPerson(str, Enum):
    first = 'first'
    second = 'second'
    third = 'third'


class DefaultPlurality(str, Enum):
    single = 'single'
    plural = 'plural'


class DefaultGender(str, Enum):
    neutral = 'neutral'
    feminine = 'feminine'
    masculine = 'masculine'


class DefaultPoliteness(str, Enum):
    casual = 'casual'
    formal = 'formal'


class Translation(BaseModel):
    """
    Translation of a Word.

    The `languageCode` should be the language that the translations is in,
    not the code of the word being translated.
    """

    id: Optional[str] = None
    word: Optional[str] = None  # UUID of Word object
    languageCode: str
    meanings: List[str]


class Word(BaseModel):
    """
    Basic unit of the project.
    Do not override this in the language-specific configurations.
    """

    id: Optional[str] = None  # UUID; string allows for serialization to JSON
    frequency: Optional[int] = None
    languageCode: str
    baseWord: str
    translations: Optional[List[Translation]] = None
    type: Any  # Allows for dynamically-created types

    def __hash__(self):
        return hash(f'{self.languageCode}-{self.baseWord}')

    def __eq__(self, other: Any) -> bool: 
        """
        Two words are equal when their languageCode and baseWord are the same.
        """
        if isinstance(other, BaseModel): 
            self_type = self.__pydantic_generic_metadata__['origin'] or self.__class__
            other_type = other.__pydantic_generic_metadata__['origin'] or other.__class__

            return (
                self_type == other_type and (
                    self.__dict__ == other.__dict__ or (
                        self.languageCode == other.languageCode and
                        self.baseWord == other.baseWord
                    )
                )
            )
        return False

    def set_id(self):
        """
        Set the id for the Word and all ids for the type.
        """
        if not self.id:
            self.id = str(uuid.uuid4())
        if not self.type.id:
            self.type.id = str(uuid.uuid4())
        for data_item in self.type.data:
            if not data_item.id:
                data_item.id = str(uuid.uuid4())
        if self.translations:
            for item in self.translations:
                if not item.id:
                    item.id = str(uuid.uuid4())


def make_grammar_model(
    language_code: str,
    grammar_model_name: str,
    instantiated_classes: Optional[Dict[str, Any]]=None
):
    """
    Creates a Pydantic BaseModel of the specified grammar type.
    Looks for a config matching the language code.
    If no configuration exists, falls back to a DEFAULT.

    Example:
        NounEN = make_grammar_model('Noun', 'en')

    :grammar_model_name: base name of the grammar class (e.g., 'Verb')
    :language_code: two-character string - e.g., 'en' for English.
    :instantiated_classes: dict of classes instantiated from the partials
        listed below this function
    """

    try:
        config_func = importlib.import_module(
            f'common.models.config.{language_code}',
        )
        config = config_func.get_config()
    except ImportError:
        config = DEFAULT_CONFIG

    grammar_model_config = config.get(grammar_model_name)
    if not grammar_model_config:
        return None

    model_kwargs = {}
    for field_name, (field_type, default) in grammar_model_config.items():
        if isinstance(field_type, str):
            try:
                field = getattr(sys.modules[__name__], field_type)
            except AttributeError:
                field = instantiated_classes[field_type]
        else:
            field = field_type
        model_kwargs[field_name] = (field, default)

    return create_model(
        f'{grammar_model_name}{language_code.upper()}',
        **model_kwargs,
    )


# When importing from a file where the type isn't specified
# (e.g., frequency data), use the unknown type.
# This can be manually changed to another type later.
UnknownDataBase = partial(make_grammar_model, grammar_model_name='UnknownData')
UnknownBase = partial(make_grammar_model, grammar_model_name='Unknown')

NounDataBase = partial(make_grammar_model, grammar_model_name='NounData')
NounBase = partial(make_grammar_model, grammar_model_name='Noun')

PronounDataBase = partial(make_grammar_model, grammar_model_name='PronounData')
PronounBase = partial(make_grammar_model, grammar_model_name='Pronoun')

AdjectiveDataBase = partial(make_grammar_model, grammar_model_name='AdjectiveData')
AdjectiveBase = partial(make_grammar_model, grammar_model_name='Adjective')

AdverbDataBase= partial(make_grammar_model, grammar_model_name='AdverbData')
AdverbBase = partial(make_grammar_model, grammar_model_name='Adverb')

VerbDataBase = partial(make_grammar_model, grammar_model_name='VerbData')
VerbBase = partial(make_grammar_model, grammar_model_name='Verb')

ConjunctionDataBase = partial(make_grammar_model, grammar_model_name='ConjunctionData')
ConjunctionBase = partial(make_grammar_model, grammar_model_name='Conjunction')

ParticipleDataBase = partial(make_grammar_model, grammar_model_name='ParticipleData')
ParticipleBase = partial(make_grammar_model, grammar_model_name='Participle')
