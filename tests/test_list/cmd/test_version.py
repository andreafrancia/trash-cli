# Copyright (C) 2011-2024 Andrea Francia Trivolzio(PV) Italy
from tests.support.dirs.temp_dir import temp_dir_fixture
from tests.support.fs_fixture import real_fs_fixture
from tests.test_list.cmd.support.trash_list_user import trash_list_user

fs = real_fs_fixture
temp_dir = temp_dir_fixture
user = trash_list_user


class TestVersion:
    def test_should_output_the_version(self, user):
        user.set_version('1.2.3')

        output = user.run_trash_list('--version')

        assert output.whole_output() == 'trash-list 1.2.3\n'
