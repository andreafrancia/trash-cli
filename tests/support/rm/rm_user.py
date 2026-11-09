import os

import pytest
from six import StringIO

from tests.support.fake_fs.fake_volumes_listing import FakeVolumesListing
from trashcli.rm.main import RmFsImpl
from trashcli.rm.rm_cmd import RmCmd


class RmUser:
    def __init__(self, fs, xdg_data_home):
        self.fs = fs
        self.xdg_data_home = xdg_data_home
        self.stderr = ''
        self.volumes = []

    def run_rm(self, args):
        err = StringIO()
        environ = {'XDG_DATA_HOME': self.xdg_data_home}
        rm_cmd = RmCmd(environ=environ,
                       getuid=lambda: 123,
                       volumes_listing=FakeVolumesListing(self.volumes),
                       stderr=err,
                       file_reader=RmFsImpl(self.fs, environ,
                                            os.geteuid))
        rm_cmd.run(['trash-rm'] + args, uid=None)
        self.stderr = err.getvalue()

    def add_volume(self, path):
        self.volumes.append(path)


@pytest.fixture
def rm_user_fixture(fs, xdg_data_home):
    return RmUser(fs, xdg_data_home)
