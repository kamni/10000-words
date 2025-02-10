"""
Copyright (C) J Leadbetter <j@jleadbetter.com>
Affero GPL v3
"""

from abc import ABC, abstractmethod
from typing import Optional

from ..models.users import UserUI


class AuthInvalidError(Exception):
    pass


class AuthPort(ABC):
    """
    Handles authentication of a user
    """

    @abstractmethod
    def login(self, username: str, password: Optional[str]=None) -> UserUI:
        """
        Log a user in.

        :username: Username of the user.
        :password: Password of the user.
            Can be empty/null

        :return: UserUI:
        :raises: AuthnInvalidError if user is not sucessfully authenticated.
        """
        pass

    @abstractmethod
    def logout(self, user: UserUI):
        """
        Log a user out.
        Should not error if user is no longer logged in
        or was never logged in.

        :user: UserUI object that was logged in
        """
        pass
