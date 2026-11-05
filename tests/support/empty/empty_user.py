import pytest

from tests.support.dates import jan_11_2001
from six import StringIO

from tests.support.fake_fs.fake_volumes_listing import FakeVolumesListing
from tests.support.fakes.stub_volume_of import StubVolumeOfFs
from trashcli.empty.empty_cmd import EmptyCmd
from trashcli.empty.existing_file_remover import ExistingFileRemover
from trashcli.empty.file_system_dir_reader import FileSystemDirReader
from trashcli.fslib.protocols.fs import Fs


class EmptyUser:
    def __init__(self, fs):
        self.fs = fs
        self.stdout = ''
        self.stderr = ''

    def run_empty(self, environ):
        out = StringIO()
        err = StringIO()
        empty_cmd = EmptyCmd(
            argv0='trash-empty',
            out=out,
            err=err,
            volumes_listing=FakeVolumesListing(),
            now=lambda: jan_11_2001(),
            file_reader=self.fs,
            file_remover=ExistingFileRemover(self.fs),
            content_reader=self.fs,
            dir_reader=FileSystemDirReader(self.fs),
            version='unused',
            volumes=StubVolumeOfFs()
        )
        empty_cmd.run_cmd([], environ, uid=123)
        self.stdout = out.getvalue()
        self.stderr = err.getvalue()


@pytest.fixture
def empty_user_fixture(fs):  # type: (Fs) -> EmptyUser
    return EmptyUser(fs)
