"""
Copyright (C) J Leadbetter <j@jleadbetter.com>
Affero GPL v3
"""

from typing import Union


def str_to_bool(val: Union[str, None]) -> bool:
    """
    Convert a string to a boolean.

    Replacement for distutils.util.strtobool,
    which was deprecated in 3.10.

    :val: Case-insensitive string representing a boolean.
        Valid `True` values are 'y', 'yes', 't', 'true', 'on', '1'.
        Valid `False` values are 'n', 'no', 'f', 'false', 'off', '0', None.

    :return: Boolean based on the supplied value.
    """
    if not isinstance(val, str) and val is not None:
        raise ValueError(f'Value "{val}" must be a string')

    val = val.lower() if val else None
    if val in ('y', 'yes', 't', 'true', 'on', '1'):
        return True
    elif val in ('n', 'no', 'f', 'false', 'off', '0', None):
        return False
    else:
        raise ValueError(f'Invalid truth value "{val}"')
