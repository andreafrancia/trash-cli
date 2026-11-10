from typing import Optional, Mapping, List

import pytest

from tests.support.dates import jan_11_2001
from six import StringIO

from tests.support.fake_fs.fake_volumes_listing import FakeVolumesListing
from tests.support.fakes.stub_volume_of import StubVolumeOfFs
from trashcli.empty.empty_cmd import EmptyCmd
from trashcli.fslib.protocols.fs import Fs


class EmptyUser:
    def __init__(self,
                 fs,  # type: Fs
                 ):
        self.fs = fs
        self.stdout = ''
        self.stderr = ''
        self.volumes = []  # type: List[str]

    def run_empty(self,
                  args=None,   # type: Optional[List[str]]
                  environ=None,  # type: Optional[Mapping[str, str]]
                  ):
        if environ is None:
            environ = {}
        out = StringIO()
        err = StringIO()
        empty_cmd = EmptyCmd(
            argv0='trash-empty',
            out=out,
            err=err,
            volumes_listing=FakeVolumesListing(self.volumes),
            now=lambda: jan_11_2001(),
            environ=environ,
            fs=self.fs,
            geteuid=lambda: 123,
            version='unused',
            volumes=StubVolumeOfFs()
        )
        if args is None:
            args = []
        empty_cmd.run_cmd(args, environ, uid=123)
        self.stdout = out.getvalue()
        self.stderr = err.getvalue()

    def add_volume(self, path):  # type: (str) -> None
        self.volumes.append(path)


@pytest.fixture
def empty_user_fixture(fs):  # type: (Fs) -> EmptyUser
    return EmptyUser(fs)
