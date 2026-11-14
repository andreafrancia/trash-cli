from typing import Optional, MutableMapping, List

import pytest

from tests.support.dates import jan_11_2001
from six import StringIO

from tests.support.fake_fs.fake_volumes_listing import FakeVolumesListing
from tests.support.fakes.stub_volume_of import StubVolumeOfFs
from trashcli.empty.empty_cmd import EmptyCmd
from trashcli.empty.empty_fs import EmptyFs


class EmptyUser:
    def __init__(self,
                 fs,  # type: EmptyFs
                 ):
        self.fs = fs
        self.stdout = ''
        self.stderr = ''
        self.volumes = []  # type: List[str]
        self.environ = {}  # type: MutableMapping[str, str]

    def run_empty(self,
                  args=None,   # type: Optional[List[str]]
                  ):
        out = StringIO()
        err = StringIO()
        empty_cmd = EmptyCmd(
            argv0='trash-empty',
            out=out,
            err=err,
            volumes_listing=FakeVolumesListing(self.volumes),
            now=lambda: jan_11_2001(),
            environ=self.environ,
            fs=self.fs,
            geteuid=lambda: 123,
            version='unused',
            volumes=StubVolumeOfFs()
        )
        if args is None:
            args = []
        empty_cmd.run_cmd(args, self.environ, uid=123)
        self.stdout = out.getvalue()
        self.stderr = err.getvalue()

    def add_volume(self, path):  # type: (str) -> None
        self.volumes.append(path)

    def add_environ(self, name, value):  # type: (str, str) -> None
        self.environ[name] = value


@pytest.fixture
def empty_user_fixture(fs):  # type: (EmptyFs) -> EmptyUser
    return EmptyUser(fs)
