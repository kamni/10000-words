"""
Copyright (C) J Leadbetter <j@jleadbetter.com>
Affero GPL v3
"""

from common.utils.singleton import Singleton


class FakeStore(metaclass=Singleton):
    def __init__(self, foo: str):
        self._foo = foo

    def update_foo(self, new_foo: str):
        self._foo = new_foo


def init_foo():
    foo = FakeStore('foo')
    foo.update_foo('bar')
