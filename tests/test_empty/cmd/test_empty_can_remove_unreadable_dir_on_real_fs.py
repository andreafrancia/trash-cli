# Copyright (C) 2011-2022 Andrea Francia Bereguardo(PV) Italy
import pytest

from tests.support.empty.empty_user import empty_user_fixture
from tests.support.fs_fixture import real_fs_fixture
from tests.support.unreadable import unreadable_fixture
from tests.support.dirs.temp_dir import temp_dir_fixture_fs

temp_dir = temp_dir_fixture_fs
unreadable = unreadable_fixture
user = empty_user_fixture
fs = real_fs_fixture


@pytest.mark.slow
class TestEmptyCanRemoveUnreadableDirOnRealFs:

    def test_trash_empty_will_skip_unreadable_dir(self,
                                                  user,
                                                  temp_dir,
                                                  unreadable):
        unreadable.new_unreadable_dir(temp_dir / 'data/Trash/files/unreadable')

        user.run_empty(environ={'XDG_DATA_HOME': temp_dir / 'data'})

        assert ("trash-empty: cannot remove %s\n" % (temp_dir / 'data/Trash/files/unreadable') ==
                user.stderr)
