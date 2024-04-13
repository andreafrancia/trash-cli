# Copyright (C) 2011-2024 Andrea Francia Trivolzio(PV) Italy

from tests.support.asserts import assert_equals_with_unidiff
from tests.support.my_path import MyPath
from tests.test_list.cmd.support.trash_list_user import TrashListUser


class TestVersion:
    def setup_method(self):
        self.user = TrashListUser(MyPath.make_temp_dir())

    def test_should_output_the_version(self):
        self.user.set_version('1.2.3')

        output = self.user.run_trash_list('--version')

        assert_equals_with_unidiff('trash-list 1.2.3\n',
                                   output.whole_output())
