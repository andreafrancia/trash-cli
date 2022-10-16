import unittest

import six

import pytest
from mock import Mock
from trashcli.restore import TrashDirectory

from ..support.files import make_file, require_empty_dir
from ..support.my_path import MyPath


@pytest.mark.slow
class TestTrashDirectory(unittest.TestCase):
    def setUp(self):
        self.temp_dir = MyPath.make_temp_dir()
        require_empty_dir(self.temp_dir / 'trash-dir')
        self.trash_dir = TrashDirectory()
        self.logger = Mock()
        self.trash_dir.logger = self.logger

    def test_should_list_a_trashinfo(self):
        make_file(self.temp_dir / 'trash-dir/info/foo.trashinfo')

        result = self.list_trashinfos()

        assert [('trashinfo', self.temp_dir / 'trash-dir/info/foo.trashinfo')] == result

    def test_should_list_multiple_trashinfo(self):
        make_file(self.temp_dir / 'trash-dir/info/foo.trashinfo')
        make_file(self.temp_dir / 'trash-dir/info/bar.trashinfo')
        make_file(self.temp_dir / 'trash-dir/info/baz.trashinfo')

        result = self.list_trashinfos()

        six.assertCountEqual(self,
                             [('trashinfo', self.temp_dir / 'trash-dir/info/foo.trashinfo'),
                              ('trashinfo', self.temp_dir / 'trash-dir/info/baz.trashinfo'),
                              ('trashinfo', self.temp_dir / 'trash-dir/info/bar.trashinfo')],
                             result)

    def test_non_trashinfo_should_reported_as_a_warn(self):
        make_file(self.temp_dir / 'trash-dir/info/not-a-trashinfo')

        result = self.list_trashinfos()

        six.assertCountEqual(self,
                             [('non_trashinfo',
                               self.temp_dir / 'trash-dir/info/not-a-trashinfo')],
                             result)

    def list_trashinfos(self):
        return list(self.trash_dir.all_info_files(self.temp_dir / 'trash-dir'))

    def tearDown(self):
        self.temp_dir.clean_up()
