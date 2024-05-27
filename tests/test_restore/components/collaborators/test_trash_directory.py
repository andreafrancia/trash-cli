import unittest

import pytest
import six

from tests.support.dirs.my_path import MyPath
from tests.support.fs_fixture import FsFixture
from trashcli.put.fs.real_fs import RealFs
from trashcli.restore.info_files import InfoFiles


@pytest.mark.slow
class TestTrashDirectory(unittest.TestCase):
    def setUp(self):
        self.temp_dir = MyPath.make_temp_dir()
        fs = RealFs()
        self.info_files = InfoFiles(fs)
        self.fx = FsFixture(fs)
        self.fx.require_empty_dir(self.temp_dir / 'trash-dir')

    def test_should_list_a_trashinfo(self):
        self.fx.make_empty_file(self.temp_dir / 'trash-dir/info/foo.trashinfo')

        result = self.list_trashinfos()

        assert [('trashinfo', self.temp_dir / 'trash-dir/info/foo.trashinfo')] == result

    def test_should_list_multiple_trashinfo(self):
        self.fx.make_empty_file(self.temp_dir / 'trash-dir/info/foo.trashinfo')
        self.fx.make_empty_file(self.temp_dir / 'trash-dir/info/bar.trashinfo')
        self.fx.make_empty_file(self.temp_dir / 'trash-dir/info/baz.trashinfo')

        result = self.list_trashinfos()

        six.assertCountEqual(self,
                             [('trashinfo', self.temp_dir / 'trash-dir/info/foo.trashinfo'),
                              ('trashinfo', self.temp_dir / 'trash-dir/info/baz.trashinfo'),
                              ('trashinfo', self.temp_dir / 'trash-dir/info/bar.trashinfo')],
                             result)

    def test_non_trashinfo_should_reported_as_a_warn(self):
        self.fx.make_empty_file(self.temp_dir / 'trash-dir/info/not-a-trashinfo')

        result = self.list_trashinfos()

        six.assertCountEqual(self,
                             [('non_trashinfo',
                               self.temp_dir / 'trash-dir/info/not-a-trashinfo')],
                             result)

    def list_trashinfos(self):
        return list(self.info_files.all_info_files(self.temp_dir / 'trash-dir'))

    def tearDown(self):
        self.temp_dir.clean_up()
