"""
Copyright (C) J Leadbetter <j@jleadbetter.com>
Affero GPL v3
"""

import string
from collections.abc import Callable
from typing import List, Optional

from nicegui import ui

from frontend.widgets.base import BaseWidget


class ValidationError(Exception):
    """
    Thrown when an input fails to validate
    """
    pass


class ValidatingInput(BaseWidget):
    """
    Input that runs validation on the content.
    """

    def __init__(
        self,
        title: str,
        marker: str,
        validators: Optional[List[Callable]]=None,
        show_title_in_errors: Optional[bool]=True,
        **kwargs,
    ):
        self._title = title
        self._marker = marker
        self._validators = validators or []
        self._input_kwargs = kwargs
        self._include_title = show_title_in_errors

        self._input = None
        self._error = None

    @property
    def value(self) -> Optional[str]:
        return self._input.value if self._input else None

    def display(self):
        self._input = ui.input(self._title, **self._input_kwargs).classes(
            'self-center',
        )
        self._error = ui.html('').mark(f'{self._marker}-errors').classes(
            'text-amber-600 text-center self-center height-fit hidden',
        )

    def add_validator(self, validator: Callable):
        self._validators.append(validator)

    def remove_validators(self):
        self._validators = []

    def validate(self):
        self.clear_errors()
        value = self._input.value
        errors = []
        for validate in self._validators:
            try:
                validate(value)
            except ValidationError as exc:
                errors.append(str(exc))

        if errors:
            self.set_error(set(errors))
            return False

        return True

    def clear_errors(self):
        """
        Clear the existing errors.
        """

        self._error.classes(add='hidden')
        self._error.text = ''

    def set_error(self, errors: List[str], include_title: Optional[bool]=True):
        """
        Set an error in the widget.

        :errors: A list of error messages to display.
        :include_title: Include the title of the field in error messages.
        """

        error_msg = '<br>'.join([
            f'{self._title + " " if include_title or self._include_title else ""}{msg}'
            for msg in errors
        ])
        self._error.content = error_msg
        self._error.classes(remove='hidden')


def text_has_min_length(text: str, expected_length: int):
    """
    Verify the text is at least an expected length.

    :text: String to validate.
    :expected_length: how long the string should be

    :return: None, if valid
    :raises: ValidationError if string is too short.
    """

    if not len(text.strip()) > expected_length - 1:
        raise ValidationError(
            f'must be at least {expected_length} characters long.',
        )


def text_does_not_contain_spaces(text: str):
    """
    Verify the text does not contain whitespace.

    :text: String to validate.

    :return: None, if valid
    :raises: ValidationError if string has whitespace
    """

    if any([char in text for char in string.whitespace]):
        raise ValidationError('must not contain spaces.')


def text_is_lowercase(text: str):
    """
    Verify the text is lowercase.

    :text: String to validate

    :return: None, if valid
    :raises: ValidationError if string has upperchase characters
    """

    if text != text.lower():
        raise ValidationError('must be lowercase.')


def text_is_alphanumeric(text: str):
    """
    Verify the text is only numbers and ascii letters,
    plus dash and underscore.

    :text: String to validate

    :return: None, if valid
    :raises: ValidationError if string isn't alphanumeric.
    """

    allowed_chars = string.ascii_lowercase + string.digits + '-_'
    if not all([char in allowed_chars for char in text]):
        raise ValidationError(
            'must have only ASCII letters, numbers, and dashes or underscores.',
        )


def text_equals_value(text: str, expected_value: str):
    """
    Verify the text matches a certain value.

    :text: String to validate.
    :expected_value: What the text should match.

    :return: None, if valid.
    :raises: ValidationError if string doesn't match.
    """

    if text != expected_value:
        raise ValidationError("doesn't match.")
