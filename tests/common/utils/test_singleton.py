"""
Copyright (C) J Leadbetter <j@jleadbetter.com>
Affero GPL v3
"""

from unittest import TestCase

from common.utils.singleton import Singleton


class Foo(metaclass=Singleton):
    def __init__(self, num: int):
        self.foo = num


class Bar(metaclass=Singleton):
    def __init__(self, foo: str):
        self.bar = foo


class TestSingleton(TestCase):
    """
    Tests for common.utils.singleton.Singleton
    """

    def tearDown(self):
        Singleton.destroy(Foo)

    def test_class_is_singleton(self):
        expected_num = 3
        foo = Foo(expected_num)
        self.assertEqual(
            expected_num,
            foo.foo,
        )

        # This shouldn't update the num
        foo2 = Foo(12345)
        self.assertEqual(
            expected_num,
            foo.foo,
        )

    def test_destroy(self):
        expected_foo = Foo(3)
        self.assertTrue(Foo in Singleton._instances)
        self.assertEqual(
            expected_foo,
            Singleton._instances[Foo],
        )

        Singleton.destroy(Foo)
        self.assertFalse(Foo in Singleton._instances)

        # Creating a new one updates the settings
        expected_num = 12345
        foo = Foo(expected_num)
        self.assertTrue(Foo in Singleton._instances)
        self.assertEqual(
            expected_num,
            foo.foo,
        )

    def test_destroy_class_does_not_exist(self):
        self.assertFalse(TestCase in Singleton._instances)
        # We shouldn't get any errors
        Singleton.destroy(TestCase)

    def test_destroy_all(self):
        foo = Foo(4)
        bar = Bar('test1')

        foo2 = Foo(5)
        bar2 = Bar('test2')
        self.assertEqual(4, foo2.foo)
        self.assertEqual('test1', bar2.bar)

        Singleton.destroy_all()

        foo3 = Foo(6)
        bar3 = Bar('test3')
        self.assertEqual(6, foo3.foo)
        self.assertEqual('test3', bar3.bar)
