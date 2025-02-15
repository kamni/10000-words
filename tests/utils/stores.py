"""
Copyright (C) J Leadbetter <j@jleadbetter.com>
Affero GPL v3
"""

from common.utils.singleton import Singleton


class FakeStore(metaclass=Singleton):
    def __init__(self, **kwargs):
        self._foo = kwargs.get('foo')

    def update_foo(self, new_foo: str):
        self._foo = new_foo


class FakeErrorStore(metaclass=Singleton):
    def __init__(self, **kwargs):
        raise Exception('Testing an exception on init')


def init_foo():
    foo = FakeStore(foo='foo')
    foo.update_foo('bar')
