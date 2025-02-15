from enum import StrEnum

from langcodes.registry_parser import parse_registry


# ISO 639 language codes as an abbreviation:abbreviation enum format
LanguageCode = StrEnum(
    'LanguageCode',
    {
        data['Subtag'].lower(): data['Subtag'].lower()
        for data in parse_registry()
        if data['Type'] == 'language' and
        data['Subtag'] != 'mro'  # Disallowed key in Python Enum
    },
)

# ISO 639 language codes in abbreviation:name dictionary format
language_code_choices = {
    data['Subtag'].lower(): data['Description'][0]
    for data in parse_registry()
    if data['Type'] == 'language' and
    data['Subtag'] != 'mro'  # Disallowed key in Python Enum
}
