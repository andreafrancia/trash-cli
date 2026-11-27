# Copyright (C) 2011-2022 Andrea Francia Bereguardo(PV) Italy
import pytest

from tests.support.dates import jan_11_2001
from tests.support.fake_fs.fake_volumes_listing import FakeVolumesListing
from six import StringIO

from tests.support.fakes.stub_volume_of import StubVolumeOfFs
from tests.support.fs_fixture import FsFixture, real_fs_fixture
from tests.support.dirs.temp_dir import temp_dir_fixture
from trashcli.empty.empty_cmd import EmptyCmd
from trashcli.empty.existing_file_remover import ExistingFileRemover
from trashcli.empty.file_system_dir_reader import FileSystemDirReader

fs = real_fs_fixture
temp_dir = temp_dir_fixture


@pytest.mark.slow
class TestTrashEmptyCmdFs:

    @pytest.fixture(autouse=True)
    def setup_fs(self, fs, temp_dir):
        self.fsx = FsFixture(fs)
        self.unreadable_dir = temp_dir / 'data/Trash/files/unreadable'
        self.err = StringIO()
        self.environ = {'XDG_DATA_HOME': temp_dir / 'data'}
        self.empty = EmptyCmd(
            argv0='trash-empty',
            out=StringIO(),
            err=self.err,
            volumes_listing=FakeVolumesListing([self.unreadable_dir]),
            now= jan_11_2001,
            file_reader=fs,
            file_remover=ExistingFileRemover(fs),
            content_reader=fs,
            dir_reader=FileSystemDirReader(fs),
            version='unused',
            volumes=StubVolumeOfFs()
        )

    def test_trash_empty_will_skip_unreadable_dir(self):
        self.fsx.make_unreadable_dir(self.unreadable_dir)

        self.empty.run_cmd([], self.environ, uid=123)

        assert ("trash-empty: cannot remove %s\n" % self.unreadable_dir ==
                self.err.getvalue())

        self.fsx.make_readable(self.unreadable_dir)
