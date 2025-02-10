"""
Copyright (C) J Leadbetter <j@jleadbetter.com>
Affero GPL v3
"""

from fastapi import Request
from fastapi.responses import RedirectResponse
from nicegui import app, ui
from starlette.middleware.base import BaseHTTPMiddleware


# We have to set /configure and /register as unrestricted,
# because they need to be accessible for initial settings creation
# and user registration.
# The /configure and /register endpoints will handle their own redirection.
UNRESTRICTED_PAGE_ROUTES = {'/', '/configure', '/register'}


class AuthMiddleware(BaseHTTPMiddleware):
    """
    Restricts access to other pages in the app.

    Modified from:
    https://github.com/zauberzeug/nicegui/tree/main/examples/authentication/main.py
    """

    async def dispatch(self, request: Request, call_next):
        import pdb; pdb.set_trace()
        if not app.storage.user.get('authenticated', False):
            if (
                not request.url.path.startswith('/_nicegui')
                and request.url.path not in UNRESTRICTED_PAGE_ROUTES
            ):
                # Remember where the user wanted to go
                app.storage.user['referrer_path'] = request.url.path
                return RedirectResponse('/')
        return await call_next(request)
