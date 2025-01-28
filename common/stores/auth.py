"""
Copyright (C) J Leadbetter <j@jleadbetter.com>
Affero GPL v3
"""

from common.utils.singleton import Singleton


class AuthStore(metaclass=Singleton):
    """
    Singleton for tracking logins/logouts
    """
