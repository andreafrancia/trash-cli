import os
from typing import MutableMapping, List

import pytest
from six import StringIO

from tests.support.fake_fs.fake_volumes_listing import FakeVolumesListing
from trashcli.fslib.protocols.fs import Fs
from trashcli.rm.main import RmFsImpl
from trashcli.rm.rm_cmd import RmCmd


class RmUser:
    def __init__(self, fs):  # type: (Fs) -> None
        self.fs = fs
        self.stderr = ''   # type: str
        self.volumes = []  # type: List[str]
        self.environ = {}  # type: MutableMapping[str, str]

    def run_rm(self, args):
        err = StringIO()
        rm_cmd = RmCmd(environ=self.environ,
                       getuid=lambda: 123,
                       volumes_listing=FakeVolumesListing(self.volumes),
                       stderr=err,
                       rm_fs=RmFsImpl(self.fs, self.environ,
                                      os.geteuid))
        rm_cmd.run(['trash-rm'] + args, uid=None)
        self.stderr = err.getvalue()

    def add_volume(self, path):  # type: (str) -> None
        self.volumes.append(path)

    def add_environ(self, name, value):  # type: (str, str) -> None
        self.environ[name] = value


@pytest.fixture
def rm_user_fixture(fs):  # type: (Fs) -> RmUser
    return RmUser(fs)
