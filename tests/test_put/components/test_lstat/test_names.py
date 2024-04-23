import getpass
import os

import grp

from trashcli.put.fs.real_fs import Names


class TestNames:
    def setup_method(self):
        self.names = Names()

    def test_username(self):
        assert self.names.username(os.getuid()) == getpass.getuser()

    def test_username_when_not_found(self):
        assert self.names.username(-1) is None

    def test_group(self):
        assert self.names.groupname(os.getgid()) == _current_group()

    def test_group_when_not_found(self):
        # this test will fail if run on a system where 99999 is the gid of
        # a group
        assert self.names.groupname(99999) is None


def _current_group():
    return grp.getgrgid(os.getgid()).gr_name
