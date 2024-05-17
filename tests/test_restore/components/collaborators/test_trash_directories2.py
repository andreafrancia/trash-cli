import unittest

import pytest
from mock import Mock, call

from tests.support.fakes.stub_volume_of import StubVolumeOf
from trashcli.restore.trash_directories import TrashDirectories2


@pytest.mark.slow
class TestTrashDirectories2(unittest.TestCase):
    def setUp(self):
        self.trash_directories = Mock(spec=['all_trash_directories'])
        self.volumes = StubVolumeOf()
        self.trash_directories2 = TrashDirectories2(
            self.volumes,
            self.trash_directories,
        )

    def test_when_user_dir_is_none(self):
        self.trash_directories.all_trash_directories.return_value = \
            "os-trash-directories"

        result = self.trash_directories2.trash_directories_or_user(None)

        self.assertEqual([call.all_trash_directories()],
                         self.trash_directories.mock_calls)
        self.assertEqual('os-trash-directories', result)

    def test_when_user_dir_is_specified(self):
        self.trash_directories.all_trash_directories.return_value = \
            "os-trash-directories"

        result = self.trash_directories2.trash_directories_or_user(
            'user-trash_dir')

        self.assertEqual([], self.trash_directories.mock_calls)
        self.assertEqual([('user-trash_dir', 'volume_of user-trash_dir')],
                         result)
