from enum import StrEnum

from langcodes.registry_parser import parse_registry


# ISO 639 language codes
LanguageCode = StrEnum(
    'LanguageCode',
    {
        data['Subtag']: data['Subtag'].lower()
        for data in parse_registry()
        if data['Type'] == 'language' and
        data['Subtag'] != 'mro'  # Disallowed key in Python Enum
    },
)
