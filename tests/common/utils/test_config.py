"""
Copyright (C) J Leadbetter <j@jleadbetter.com>
Affero GPL v3
"""

from unittest import TestCase

from common.utils.config import str_to_bool


class TestStrToBool(TestCase):
    """
    Tests for common.utils.config.str_to_bool
    """

    def test_true(self):
        true_values = ['y', 'yes', 't', 'true', 'on', '1']
        for val in true_values:
            self.assertTrue(str_to_bool(val))
            self.assertTrue(str_to_bool(val.title()))
            self.assertTrue(str_to_bool(val.upper()))

    def test_false(self):
        false_values = ['n', 'no', 'f', 'false', 'off', '0']
        for val in false_values:
            self.assertFalse(str_to_bool(val))
            self.assertFalse(str_to_bool(val.title()))
            self.assertFalse(str_to_bool(val.upper()))
        self.assertFalse(str_to_bool(None))

    def test_not_valid(self):
        for val in [0, 1, 'foo', [], {}]:
            with self.assertRaises(ValueError):
                str_to_bool(val)
