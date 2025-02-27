"""
Copyright (C) J Leadbetter <j@jleadbetter.com>
Affero GPL v3
"""

from typing import Any, Dict, List, Optional

from nicegui import app

from common.models.users import UserDB, UserUI
from frontend.controllers.base import BaseController


class UserController(BaseController):
    """
    Control state of the current user in the application
    """

    @property
    def backend_adapter(self):
        if not self._backend_adapter:
            self._backend_adapter = self.adapters.get('UserDBPort')
        return self._backend_adapter

    @property
    def frontend_adapter(self):
        if not self._frontend_adapter:
            self._frontend_adapter = self.adapters.get('UserUIPort')
        return self._frontend_adapter

    def get(self) -> Optional[UserUI]:
        user_dict = app.storage.user
        if 'id' in user_dict:
            user = UserUI(**user_dict)
            return user
        return None

    def get_all(self) -> List[UserUI]:
        userdbs = self.backend_adapter.get_all()
        if userdbs:
            return self.frontend_adapter.get_all(userdbs)
        return []

    def get_first(self) -> Optional[UserUI]:
        userdb = self.backend_adapter.get_first()
        if userdb:
            return self.frontend_adapter.get(userdb)
        return None

    def reset(self):
        app.storage.user.clear()

    def set(self, user: UserUI):
        if not user.authenticated:
            user.authenticated = True
        app.storage.user.update(user.model_dump())

    def update(self, user_dict: Dict[str, Any]):
        user = UserDB(
            display_name=user_dict.get('display_name'),
            username=user_dict.get('username'),
            password=user_dict.get('password'),
            is_admin=user_dict.get('is_admin'),
        )
        self.backend_adapter.create(user)
