"""
Copyright (C) J Leadbetter <j@jleadbetter.com>
Affero GPL v3
"""

import os
import uuid
from pathlib import Path
from unittest import TestCase

from common.models.documents import DocumentDB
from common.stores.config import ConfigStore
from common.utils.files import get_project_dir, get_upload_dir
from common.utils.singleton import Singleton


TEST_DIR = Path(__file__).resolve().parent.parent.parent
TEST_CONFIG = TEST_DIR / 'setup.cfg'


class TestGetProjectDir(TestCase):
    """
    Tests for common.utils.files.get_project_dir
    """

    def test_get_project_dir(self):
        expected = Path(__file__).resolve().parent.parent.parent.parent
        returned = get_project_dir()
        self.assertEqual(expected, returned)


class TestGetUploadDir(TestCase):
    """
    Tests for common.utils.files.get_upload_dir
    """

    def setUp(self):
        Singleton.destroy(ConfigStore)

    def tearDown(self):
        Singleton.destroy(ConfigStore)

    def test_get_absolute_path(self):
        config = ConfigStore(TEST_CONFIG, 'test')
        expected_path = Path(config.get('common', 'UploadDir'))
        returned_path = get_upload_dir()
        self.assertEqual(expected_path, returned_path)

    def test_get_from_relative_path(self):
        config = ConfigStore(TEST_CONFIG, 'dev.django')
        expected_path = TEST_DIR.parent / config.get('common', 'UploadDir')
        returned_path = get_upload_dir()
        self.assertEqual(expected_path, returned_path)
