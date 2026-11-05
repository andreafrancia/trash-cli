# Copyright (C) 2011-2022 Andrea Francia Bereguardo(PV) Italy
import pytest

from tests.support.empty.empty_user import empty_user_fixture
from tests.support.fs_fixture import fake_fs_fixture
from tests.support.unreadable import unreadable_fixture

fs = fake_fs_fixture
unreadable = unreadable_fixture
user = empty_user_fixture

class TestEmptyCanRemoveUnreadableDir:
    @pytest.fixture(autouse=True)
    def setup_environ(self):
        self.tmp_dir = '/tmp'
        self.unreadable_dir = self.tmp_dir + '/data/Trash/files/unreadable'
        self.environ = {'XDG_DATA_HOME': self.tmp_dir + '/data'}

    def test_trash_empty_will_skip_unreadable_dir(self,
                                                  user,
                                                  unreadable):
        unreadable.new_unreadable_dir(self.unreadable_dir)

        user.run_empty([], self.environ)

        assert ("trash-empty: cannot remove %s\n" % self.unreadable_dir ==
                user.stderr)
