# Copyright (C) 2011-2022 Andrea Francia Bereguardo(PV) Italy
import os

import pytest

from tests.support.empty.empty_user import empty_user_fixture
from tests.support.fs_fixture import real_fs_fixture
from tests.support.unreadable import unreadable_fixture
from tests.support.dates import jan_11_2001
from six import StringIO

from tests.support.fake_fs.fake_volumes_listing import FakeVolumesListing
from tests.support.fakes.stub_volume_of import StubVolumeOfFs
from tests.support.dirs.temp_dir import make_temp_dir, temp_dir_fixture_fs
from trashcli.empty.empty_cmd import EmptyCmd
from trashcli.empty.existing_file_remover import ExistingFileRemover
from trashcli.empty.file_system_dir_reader import FileSystemDirReader
from trashcli.fslib.real.real_fs import RealFs



temp_dir = temp_dir_fixture_fs
unreadable = unreadable_fixture
user = empty_user_fixture
fs = real_fs_fixture

@pytest.mark.slow
class TestTrashEmptyCmdFs:

    def test_trash_empty_will_skip_unreadable_dir(self,
                                                  user,
                                                  temp_dir,
                                                  unreadable):
        unreadable.new_unreadable_dir(temp_dir / 'data/Trash/files/unreadable')

        user.run_empty(environ={'XDG_DATA_HOME': temp_dir / 'data'})

        assert ("trash-empty: cannot remove %s\n" % (temp_dir / 'data/Trash/files/unreadable') ==
                user.stderr)

@pytest.mark.slow
class TestTrashEmptyRemovesReadonlyDir:
    def setup_method(self):
        self.fs = RealFs()
        self.tmp_dir = make_temp_dir(self.fs)
        self.trash_files = self.tmp_dir / 'data/Trash/files'
        self.err = StringIO()
        self.environ = {'XDG_DATA_HOME': self.tmp_dir / 'data'}
        self.empty = EmptyCmd(
            argv0='trash-empty',
            out=StringIO(),
            err=self.err,
            volumes_listing=FakeVolumesListing(),
            now=lambda: jan_11_2001(),
            file_reader=self.fs,
            file_remover=ExistingFileRemover(self.fs),
            content_reader=self.fs,
            dir_reader=FileSystemDirReader(self.fs),
            version='unused',
            volumes=StubVolumeOfFs()
        )

    def test_a_directory_without_write_permission_is_removed(self):
        target = self.trash_files / 'proj'
        self.fs.makedirs(target / 'sub', 0o755)
        self.fs.write_file(target / 'sub' / 'f', 'x')
        self.fs.chmod(target / 'sub', 0o500)
        self.fs.chmod(target, 0o500)

        self.empty.run_cmd([], self.environ, uid=123)

        assert not self.fs.path_exists(target)
        assert self.err.getvalue() == ""

    def teardown_method(self):
        # restore write bits so a failed run can still be cleaned up
        for root, dirs, files in self.fs.walk_no_follow(self.trash_files):
            for name in dirs:
                self.fs.chmod(os.path.join(root, name), 0o700)
        self.tmp_dir.clean_up()
