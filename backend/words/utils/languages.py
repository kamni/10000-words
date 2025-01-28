"""
Copyright (C) J Leadbetter <j@jleadbetter.com>
Affero GPL v3
"""

from django.db import models
from langcodes.registry_parser import parse_registry

from common.utils.languages import LanguageCode


# ISO 639 language codes
language_code_choices = {
    data['Subtag']: data['Description'][0].lower()
    for data in parse_registry()
    if data['Type'] == 'language' and
    data['Subtag'] != 'mro'  # Disallowed key in Python Enum
}
